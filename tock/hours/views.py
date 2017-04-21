import csv
import datetime
import io
from itertools import chain
from operator import attrgetter

# Create your views here.
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.db.models import Prefetch, Q, Sum
from django.contrib.auth.decorators import user_passes_test

from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

from api.views import get_timecards, TimecardList, ProjectSerializer, UserDataSerializer
from api.renderers import stream_csv
from employees.models import UserData
from projects.models import AccountingCode
from tock.remote_user_auth import email_to_username
from tock.utils import PermissionMixin, IsSuperUserOrSelf

from .models import ReportingPeriod, Timecard, TimecardObject, Project, Targets
from .forms import (
    ReportingPeriodForm,
    ReportingPeriodImportForm,
    projects_as_choices,
    TimecardForm,
    TimecardFormSet,
    timecard_formset_factory
)
from utilization.utils import calculate_utilization, get_fy_first_day

class DashboardReportsList(ListView):
    template_name = 'hours/dashboard_list.html'

    def get_queryset(self):
        available_reports = ReportingPeriod.objects.filter(
            start_date__gte=datetime.date(2016, 10, 1),
            end_date__lt=datetime.date.today()
        )
        return available_reports

class DashboardView(TemplateView):
    template_name = 'hours/dashboard.html'

    def get_context_data(self, **kwargs):

        # Helper functions.
        def clean_result(result):
            if result:
                pass
            else:
                result = 0
            return result

        def calc_result(performance, target):
            try:
                variance = float(performance) - float(target)
                p_variance = variance / target
                return variance, p_variance
            except ZeroDivisionError:
                return 0, 0

        def get_params(key):
            try:
                param = self.request.GET[key]
            except KeyError:
                param = None
            return param

        # Get base context.
        context = super(DashboardView, self).get_context_data(**kwargs)

        # Get unit param.
        unit_param = None #get_params('unit')

        # Get requested date and corresponding reporting period.
        requested_date = datetime.datetime.strptime(
            self.kwargs['reporting_period'], "%Y-%m-%d"
        ).date()
        try:
            rp_selected = ReportingPeriod.objects.get(
                start_date__lte=requested_date,
                end_date__gte=requested_date
            )
            rp_selected.future_date = rp_selected.end_date + datetime.timedelta(
                weeks=13
            )
        except ReportingPeriod.DoesNotExist:
            context.update(
                {
                    'error':'No reporting period available for {}.'\
                    .format(self.kwargs['reporting_period'])
                }
            )
            return context

        # Get all current employees.
        employees = UserData.objects.filter(
            is_18f_employee=True,
            current_employee=True
        ).exclude(unit__in=[4, 9, 14, 15])
        units = []
        missing_units = []
        for e in employees:
            if e.unit:
                units.append(
                    (e.unit, e.get_unit_display())
                )
            else:
                missing_units.append(e)

        units = sorted(set(units), key=lambda x: x[1])

        # Narrow to unit employees, if applicable.
        if unit_param:
            all_count = employees.count()
            employees = employees.filter(unit=unit_param)
            org_proportion = employees.count() / all_count
        else:
            org_proportion = 1

        # Get calendar info.
        fytd_start_date = get_fy_first_day(requested_date)
        percent_of_year = ((requested_date - fytd_start_date).days) / 365

        # Get initial targets.
        try:
            target = Targets.objects.get(
                start_date__lte=rp_selected.start_date,
                end_date__gte=rp_selected.end_date
            )
        except Targets.DoesNotExist:
            context.update(
                {
                    'error':'No target information available for {}.'\
                    .format(self.kwargs['reporting_period'])
                }
            )
            return context

        # Calculated targets.
        hours_required_cr_fytd = \
            target.hours_target_cr * percent_of_year * org_proportion
        hours_required_plan_fytd = \
            target.hours_target_plan * percent_of_year * org_proportion
        revenue_required_cr_fytd = \
            target.revenue_target_cr * percent_of_year * org_proportion
        revenue_required_plan_fytd = \
            target.revenue_target_plan * percent_of_year * org_proportion
        hours_required_cr_weekly = \
            (target.hours_target_cr / target.periods) * org_proportion
        hours_required_plan_weekly = \
            (target.hours_target_plan / target.periods) * org_proportion
        revenue_required_cr_weekly = \
            (target.revenue_target_cr / target.periods) * org_proportion
        revenue_required_plan_weekly = \
            (target.revenue_target_plan / target.periods) * org_proportion

        # Get hours billed for fiscal year to date and clean result.
        hours_billed_fytd = clean_result(TimecardObject.objects.filter(
            timecard__reporting_period__start_date__gte=fytd_start_date,
            timecard__reporting_period__end_date__lte=requested_date,
            project__accounting_code__billable=True,
            timecard__user__user_data__in=employees
        ).exclude(
            project__profit_loss_account__name='FY17 Acquisition Svcs Billable'
        ).aggregate(Sum('hours_spent'))['hours_spent__sum'])
        rev_fytd = hours_billed_fytd * target.labor_rate

        # Get data for reporting period and clean result.
        hours_billed_weekly = clean_result(TimecardObject.objects.filter(
            timecard__reporting_period__start_date=\
                rp_selected.start_date.strftime('%Y-%m-%d'),
            project__accounting_code__billable=True,
            timecard__user__user_data__in=employees
        ).exclude(
            project__profit_loss_account__name='FY17 Acquisition Svcs Billable'
        ).aggregate(Sum('hours_spent'))['hours_spent__sum'])
        rev_weekly = hours_billed_weekly * target.labor_rate

        variance_cr_ytd, p_variance_cr_fytd = calc_result(
            hours_billed_fytd, hours_required_cr_fytd
        )
        variance_plan_fytd, p_variance_plan_fytd = calc_result(
            hours_billed_fytd, hours_required_plan_fytd
        )
        variance_cr_weekly, p_variance_cr_weekly = calc_result(
            hours_billed_weekly, hours_required_cr_weekly
        )
        variance_plan_weekly, p_variance_plan_weekly = calc_result(
            hours_billed_weekly, hours_required_plan_weekly
        )
        variance_rev_cr_ytd, p_variance_rev_cr_ytd = calc_result(
            rev_fytd, revenue_required_cr_fytd
        )
        variance_rev_plan_ytd, p_variance_rev_plan_ytd = calc_result(
            rev_fytd, revenue_required_plan_fytd
        )
        variance_rev_cr_weekly, p_variance_rev_cr_weekly = calc_result(
            rev_weekly, revenue_required_cr_weekly
        )
        variance_rev_plan_weekly, p_variance_rev_plan_weekly = calc_result(
            rev_weekly, revenue_required_plan_weekly
        )

        # Update context.
        context.update(
            {   # Unit data.
                'units':units,
                'missing_units':missing_units,
                # Target info.
                'revenue_target_cr':'${:,}'.format(
                    target.revenue_target_cr
                ),
                'revenue_target_plan':'${:,}'.format(
                    target.revenue_target_plan
                ),
                # Rate info.
                'labor_rate':'${:,}'.format(
                    target.labor_rate
                ),
                # Temporal info.
                'rp_selected':rp_selected,
                'fytd_start_date':fytd_start_date,
                # Annual performance
                'hours_required_cr_fytd':'{:,}'.format(
                    round(hours_required_cr_fytd,2)
                ),
                'hours_required_plan_fytd':'{:,}'.format(
                    round(hours_required_plan_fytd,2)
                ),
                'hours_billed_fytd':'{:,}'.format(
                    round(hours_billed_fytd,2)
                ),
                'variance_cr_ytd':'{:,}'.format(
                    round(variance_cr_ytd,2)
                ),
                'variance_plan_fytd':'{:,}'.format(
                    round(variance_plan_fytd,2)
                ),
                'p_variance_cr_fytd':'{0:.2%}'.format(
                    p_variance_cr_fytd
                ),
                'p_variance_plan_fytd':'{0:.2%}'.format(
                    p_variance_plan_fytd
                ),
                'revenue_required_cr_fytd':'${:,}'.format(
                    round(revenue_required_cr_fytd)
                ),
                'revenue_required_plan_fytd':'${:,}'.format(
                    round(revenue_required_plan_fytd)
                ),
                'rev_fytd':'${:,}'.format(
                    round(rev_fytd)
                ),
                'variance_rev_cr_ytd':'${:,}'.format(
                    round(variance_rev_cr_ytd)
                ),
                'variance_rev_plan_ytd':'${:,}'.format(
                    round(variance_rev_plan_ytd)
                ),
                'p_variance_rev_cr_ytd':'{0:.2%}'.format(
                    p_variance_rev_cr_ytd
                ),
                'p_variance_rev_plan_ytd':'{0:.2%}'.format(
                    p_variance_rev_plan_ytd
                ),
                # Weekly performance.
                'hours_required_cr_weekly':'{:,}'.format(
                    round(hours_required_cr_weekly,2)
                ),
                'hours_required_plan_weekly':'{:,}'.format(
                    round(hours_required_plan_weekly,2)
                ),
                'hours_billed_weekly':'{:,}'.format(
                    round(hours_billed_weekly,2)
                ),
                'variance_cr_weekly':'{:,}'.format(
                    round(variance_cr_weekly,2)
                ),
                'variance_plan_weekly':'{:,}'.format(
                    round(variance_plan_weekly,2)
                ),
                'p_variance_cr_weekly':'{0:.2%}'.format(
                    p_variance_cr_weekly
                ),
                'p_variance_plan_weekly':'{0:.2%}'.format(
                    p_variance_plan_weekly
                ),
                'revenue_required_cr_weekly':'${:,}'.format(
                    round(revenue_required_cr_weekly)
                ),
                'revenue_required_plan_weekly':'${:,}'.format(
                    round(revenue_required_plan_weekly)
                ),
                'rev_weekly':'${:,}'.format(
                    round(rev_weekly)
                ),
                'variance_rev_cr_weekly':'${:,}'.format(
                    round(variance_rev_cr_weekly)
                ),
                'variance_rev_plan_weekly':'${:,}'.format(
                    round(variance_rev_plan_weekly)
                ),
                'p_variance_rev_cr_weekly':'{0:.2%}'.format(
                    p_variance_rev_cr_weekly
                ),
                'p_variance_rev_plan_weekly':'{0:.2%}'.format(
                    p_variance_rev_plan_weekly
                ),

            }
        )
        return context


class BulkTimecardSerializer(serializers.Serializer):
    project_name = serializers.CharField(source='project.name')
    project_id = serializers.CharField(source='project.id')
    employee = serializers.StringRelatedField(source='timecard.user')
    start_date = serializers.DateField(source='timecard.reporting_period.start_date')
    end_date = serializers.DateField(source='timecard.reporting_period.end_date')
    hours_spent = serializers.DecimalField(max_digits=5, decimal_places=2)
    billable = serializers.BooleanField(source='project.accounting_code.billable')
    agency = serializers.CharField(source='project.accounting_code.agency.name')
    flat_rate = serializers.BooleanField(source='project.accounting_code.flat_rate')
    active = serializers.BooleanField(source='project.active')
    mbnumber = serializers.CharField(source='project.mbnumber')
    notes = serializers.CharField()
    revenue_profit_loss_account = serializers.CharField(
        source='revenue_profit_loss_account.accounting_string'
    )
    revenue_profit_loss_account_name = serializers.CharField(
        source='revenue_profit_loss_account.name'
    )
    expense_profit_loss_account = serializers.CharField(
        source='expense_profit_loss_account.accounting_string'
    )
    expense_profit_loss_account_name = serializers.CharField(
        source='expense_profit_loss_account.name'
    )
class GeneralSnippetsTimecardSerializer(serializers.Serializer):
    project_name = serializers.CharField(source='project.name')
    employee = serializers.StringRelatedField(source='timecard.user')
    unit = serializers.CharField(source='timecard.user.user_data.unit')
    start_date = serializers.DateField(source='timecard.reporting_period.start_date')
    end_date = serializers.DateField(source='timecard.reporting_period.end_date')
    hours_spent = serializers.DecimalField(max_digits=5, decimal_places=2)
    notes = serializers.CharField()
    unit = serializers.SerializerMethodField()

    def get_unit(self,obj):
        try:
            unit = obj.timecard.user.user_data.get_unit_display()
        except ObjectDoesNotExist:
            unit = ''
        return unit

class SlimBulkTimecardSerializer(serializers.Serializer):
    project_name = serializers.CharField(source='project.name')
    project_id = serializers.CharField(source='project.id')
    employee = serializers.StringRelatedField(source='timecard.user')
    start_date = serializers.DateField(source='timecard.reporting_period.start_date')
    end_date = serializers.DateField(source='timecard.reporting_period.end_date')
    hours_spent = serializers.DecimalField(max_digits=5, decimal_places=2)
    billable = serializers.BooleanField(source='project.accounting_code.billable')
    mbnumber = serializers.CharField(source='project.mbnumber')

class AdminBulkTimecardSerializer(serializers.Serializer):
    project_name = serializers.CharField(source='project.name')
    project_id = serializers.CharField(source='project.id')
    employee = serializers.StringRelatedField(source='timecard.user')
    start_date = serializers.DateField(source='timecard.reporting_period.start_date')
    end_date = serializers.DateField(source='timecard.reporting_period.end_date')
    hours_spent = serializers.DecimalField(max_digits=5, decimal_places=2)
    billable = serializers.BooleanField(source='project.accounting_code.billable')
    agency = serializers.CharField(source='project.accounting_code.agency.name')
    flat_rate = serializers.BooleanField(source='project.accounting_code.flat_rate')
    active = serializers.BooleanField(source='project.active')
    mbnumber = serializers.CharField(source='project.mbnumber')
    notes = serializers.CharField()
    grade = serializers.CharField(source='grade.grade')
    revenue_profit_loss_account = serializers.CharField(
        source='revenue_profit_loss_account.accounting_string'
    )
    revenue_profit_loss_account_name = serializers.CharField(
        source='revenue_profit_loss_account.name'
    )
    expense_profit_loss_account = serializers.CharField(
        source='expense_profit_loss_account.accounting_string'
    )
    expense_profit_loss_account_name = serializers.CharField(
        source='expense_profit_loss_account.name'
    )


def user_data_csv(request):
    """
    Stream all user data as CSV.
    """
    queryset = UserData.objects.all()
    serializer = UserDataSerializer()
    return stream_csv(queryset, serializer)

def projects_csv(request):
    """
    Stream all of the projects as CSV.
    """
    queryset = Project.objects.all()
    serializer = ProjectSerializer()
    return stream_csv(queryset, serializer)

def bulk_timecard_list(request):
    """
    Stream all the timecards as CSV.
    """
    queryset = get_timecards(TimecardList.queryset, request.GET)
    serializer = BulkTimecardSerializer()
    return stream_csv(queryset, serializer)

def slim_bulk_timecard_list(request):
    """
    Stream a slimmed down version of all the timecards as CSV.
    """
    queryset = get_timecards(TimecardList.queryset, request.GET)
    serializer = SlimBulkTimecardSerializer()
    return stream_csv(queryset, serializer)

def general_snippets_only_timecard_list(request):
    """
    Stream all timecard data that is for General and has a snippet.
    """
    objects = TimecardObject.objects.filter(
        project__name='General',
        notes__isnull=False
    )
    queryset = get_timecards(objects, request.GET)
    serializer = GeneralSnippetsTimecardSerializer()
    return stream_csv(queryset, serializer)

def timeline_view(request, value_fields=(), **field_alias):
    """ CSV endpoint for the project timeline viz. """
    queryset = get_timecards(TimecardList.queryset, request.GET)

    fields = list(value_fields) + [
        'timecard__reporting_period__start_date',
        'timecard__reporting_period__end_date',
        'project__accounting_code__billable'
    ]

    field_map = {
        'timecard__reporting_period__start_date': 'start_date',
        'timecard__reporting_period__end_date': 'end_date',
        'project__accounting_code__billable': 'billable',
    }
    field_map.update(field_alias)

    data = queryset.values(*fields).annotate(hours_spent=Sum('hours_spent'))

    fields.append('hours_spent')

    data = [
        {
            field_map.get(field, field): row.get(field)
            for field in fields
        }
        for row in data
    ]

    response = HttpResponse(content_type='text/csv')

    fieldnames = [field_map.get(field, field) for field in fields]
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    return response

def project_timeline_view(request):
    return timeline_view(
        request,
        value_fields=['project__id', 'project__name'],
        project__id='project_id',
        project__name='project_name',
    )

def user_timeline_view(request):
    return timeline_view(
        request,
        value_fields=['timecard__user__username'],
        timecard__user__username='user',
    )

@user_passes_test(lambda u: u.is_superuser)
def admin_bulk_timecard_list(request):
    queryset = get_timecards(TimecardList.queryset, request.GET)
    serializer = AdminBulkTimecardSerializer()
    return stream_csv(queryset, serializer)

class ReportingPeriodListView(PermissionMixin, ListView):
    """ Currently the home view that lists the completed and missing time
    periods """
    context_object_name = "incomplete_reporting_periods"
    queryset = ReportingPeriod.objects.all()
    template_name = "hours/reporting_period_list.html"
    permission_classes = (IsAuthenticated, )

    def get_context_data(self, **kwargs):
        context = super(
            ReportingPeriodListView, self).get_context_data(**kwargs)
        try:
            unstarted_reporting_periods = self.queryset.exclude(
                timecard__user=self.request.user.id).exclude(
                end_date__lte=self.request.user.user_data.start_date)
            unfinished_reporting_periods = self.queryset.filter(
                timecard__submitted=False,
                timecard__user=self.request.user.id).exclude(
                end_date__lte=self.request.user.user_data.start_date)
        except ValueError:
            unstarted_reporting_periods = self.queryset.exclude(
                timecard__user=self.request.user)
            unfinished_reporting_periods = self.queryset.filter(
                timecard__submitted=False,
                timecard__user=self.request.user)

        context['uncompleted_reporting_periods'] = sorted(list(chain(
            unstarted_reporting_periods, unfinished_reporting_periods)),
            key=attrgetter('start_date'))
        return context

class ReportingPeriodListUserView(TemplateView):
    template_name = 'hours/reporting_period_user_list.html'

    def get_context_data(self, **kwargs):
        context = super(
            ReportingPeriodListUserView, self).get_context_data(**kwargs)

        timecards = Timecard.objects.prefetch_related(
            'reporting_period'
        ).filter(
            user=self.request.user.id
        )
        data = []
        for timecard in timecards:
            data.append(
                {
                    'reporting_period':timecard.reporting_period,
                    'timecard':timecard,
                    'actions':['View']
                }
        )
        today = datetime.date.today()
        for datum in data:
            if datum['timecard'].submitted:
                rp_end_date = datum['reporting_period'].end_date
                # If the reporting period has not ended, all actions available.
                # While this could be handled in the next if statement, there
                # could be future needs to provide additional options for
                # reporting periods that have not yet closed, for example
                # to delete the entire timecard and start again.
                if rp_end_date >= today:
                    datum['actions'].extend(['Edit'])
                # If the reporting period has ended, but was within the last 7
                # days and the timecard is submitted, edit action availble.
                elif (today - rp_end_date).days <= 7:
                    datum['actions'].append('Edit')
            else:
                # If never submitted, all actions available.
                datum['actions'].extend(['Edit'])
        data = sorted(
            data,
            key=lambda x: x['reporting_period'].start_date,
            reverse=True
        )
        context.update({'data':data})
        return context

class ReportingPeriodCreateView(PermissionMixin, CreateView):
    form_class = ReportingPeriodForm
    template_name = 'hours/reporting_period_form.html'
    permission_classes = (IsSuperUserOrSelf, )

    def get_success_url(self):
        return reverse("ListReportingPeriods")


class ReportingPeriodBulkImportView(PermissionMixin, FormView):
    template_name = 'hours/reporting_period_import.html'
    form_class = ReportingPeriodImportForm
    permission_classes = (IsSuperUserOrSelf, )

    def form_valid(self, form):
        if form.is_valid():
            reporting_period = form.cleaned_data['reporting_period']
            line_items = io.StringIO(
                self.request.FILES['line_items'].read().decode('utf-8'),
                newline=None,
            )

            c = csv.DictReader(line_items)

            for line_item in c:
                user, created = get_user_model().objects.get_or_create(
                    username=email_to_username(line_item['Tock Name'].lower()))

                timecard, created = Timecard.objects.get_or_create(
                    user=user, reporting_period=reporting_period)

                timecard.save()

                try:
                    project = Project.objects.get(id=line_item['Tock Code'])
                except Project.DoesNotExist:
                    raise ValidationError(
                        'Project %s (Code %s) Does Not Exist' %
                        (line_item['Tock Proj. Name'], line_item['Tock Code']))

                try:
                    TimecardObject.objects.get(
                        timecard=timecard,
                        project=project,
                        hours_spent=line_item['Hours Logged'])
                except TimecardObject.DoesNotExist:
                    TimecardObject.objects.create(
                        timecard=timecard,
                        project=project,
                        hours_spent=line_item['Hours Logged'])

        return super(ReportingPeriodBulkImportView, self).form_valid(form)

    def get_success_url(self):
        return reverse("ListReportingPeriods")


class TimecardView(UpdateView):
    form_class = TimecardForm
    template_name = 'hours/timecard_form.html'

    def get_object(self, queryset=None):
        self.report_date = datetime.datetime.strptime(
            self.kwargs['reporting_period'], "%Y-%m-%d"
        ).date()
        r = ReportingPeriod.objects.get(start_date=self.report_date)
        obj, created = Timecard.objects.get_or_create(
            reporting_period_id=r.id,
            user_id=self.request.user.id)
        return obj

    def get(self, request, *args, **kwargs):
        """Get timecard form only for last N reporting periods or if
        unsubmitted timecards."""

        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        if self.object.submitted == False:
            # If timecard has not been submitted, return form.
            return self.render_to_response(context)
        today = datetime.date.today()
        rp_end_date = self.object.reporting_period.end_date
        if rp_end_date > today:
            # If timecard has been submitted, but the reporting period has not
            # ended, return form.
            return self.render_to_response(context)
        elif (today - rp_end_date).days > 7:
            # If the timecard has been submitted and the end date of the
            # reporting period is greater than seven days, do not return form
            # instead return the report page.
            return redirect(
                reverse(
                    'reports:ReportingPeriodUserDetailView',
                    kwargs={
                        'username':request.user.username,
                        'reporting_period':self.kwargs['reporting_period']
                    }
                )
            )

    def get_context_data(self, **kwargs):
        context = super(TimecardView, self).get_context_data(**kwargs)

        base_reporting_period = ReportingPeriod.objects.get(
            start_date=self.kwargs['reporting_period'])

        formset = self.get_formset()
        formset.set_exact_working_hours(base_reporting_period.exact_working_hours)
        formset.set_max_working_hours(base_reporting_period.max_working_hours)
        formset.set_min_working_hours(base_reporting_period.min_working_hours)

        reporting_period = ReportingPeriod.objects.get(pk=self.object.reporting_period_id)


        accounting_codes = []

        # TODO: This is inefficient because we're writing over the
        # already-generated choices. Ideally we should be passing these
        # into the formset constructor.
        choices = projects_as_choices(reporting_period.get_projects())

        for form in formset.forms:
            form.fields['project'].choices = choices

        if self.request.POST.get('save_only') is not None:
            formset.save_only = True

        context.update({
            'exact_working_hours': base_reporting_period.exact_working_hours,
            'min_working_hours': base_reporting_period.min_working_hours,
            'max_working_hours': base_reporting_period.max_working_hours,
            'formset': formset,
            'messages': messages.get_messages(self.request),
            'unsubmitted': not self.object.submitted,
        })

        return context

    def get_formset(self):
        post = self.request.POST

        if post:
            return TimecardFormSet(post, instance=self.object)

        if self.object.timecardobjects.count() == 0:
            return self.prefilled_formset()
        return TimecardFormSet(instance=self.object)

    def last_timecard(self):
        return Timecard.objects.filter(
            reporting_period__start_date__lt=self.report_date,
            user_id=self.request.user.id,
            submitted=True,
        ).order_by(
            '-reporting_period__start_date',
        ).first()

    def prefilled_formset(self):
        timecard = self.last_timecard()
        project_ids, extra = [], 1
        if timecard:
            project_ids = set(
                tco.project_id for tco in
                timecard.timecardobjects.all()
            )
            extra = len(project_ids) + 1

        rp = ReportingPeriod.objects \
            .prefetch_related('holiday_prefills__project') \
            .get(start_date=self.kwargs['reporting_period'])

        init = []
        if rp.holiday_prefills:
            init += [
                {'hours_spent': hp.hours_per_period, 'project': hp.project.id}
                for hp in rp.holiday_prefills.all()
            ]
        init += [{'hours_spent': None, 'project': pid} for pid in project_ids]

        formset = timecard_formset_factory(extra=extra)
        return formset(initial=init)


    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.submitted = not formset.save_only
            self.object.reporting_period = ReportingPeriod.objects.get(
                start_date=self.kwargs['reporting_period'])
            self.object.save()
            formset.instance = self.object
            formset.save()
            return super(UpdateView, self).form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        if self.object.submitted:
            return reverse("ListReportingPeriods")
        else:
            messages.add_message(
                self.request,
                messages.INFO,
                'Timesheet saved.  Please remember to submit your timesheet when finished.'
            )

            return reverse(
                'reportingperiod:UpdateTimesheet',
                kwargs={'reporting_period': self.kwargs['reporting_period']}
            )


class ReportsList(ListView):

    """Show a list of all Reporting Periods to navigate to various reports"""
    template_name = "hours/reports_list.html"

    def get_queryset(self, queryset=None):
        query = ReportingPeriod.objects.all()
        fiscal_years = {}
        for reporting_period in query:
            if str(reporting_period.get_fiscal_year()) in fiscal_years:
                fiscal_years[str(
                    reporting_period.get_fiscal_year())].append(
                    reporting_period)
            else:
                fiscal_years[str(reporting_period.get_fiscal_year())] = [
                    reporting_period
                ]
        sorted_fiscal_years = sorted(fiscal_years.items(), reverse=True)
        return sorted_fiscal_years


class ReportingPeriodDetailView(ListView):
    template_name = "hours/reporting_period_detail.html"
    context_object_name = "timecard_list"

    def get_queryset(self):
        return Timecard.objects.filter(
            reporting_period__start_date=datetime.datetime.strptime(
                self.kwargs['reporting_period'],
                "%Y-%m-%d").date(),
            submitted=True,
        ).select_related(
            'user',
            'reporting_period',
        ).distinct().order_by('user__last_name', 'user__first_name')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(
            ReportingPeriodDetailView, self).get_context_data(**kwargs)
        reporting_period = ReportingPeriod.objects.get(
            start_date=datetime.datetime.strptime(
                self.kwargs['reporting_period'], "%Y-%m-%d").date())
        filed_users = list(
            Timecard.objects.filter(
                reporting_period=reporting_period,
                submitted=True
            ).distinct().all().values_list('user__id', flat=True))
        context['users_without_filed_timecards'] = get_user_model().objects \
            .exclude(user_data__start_date__gte=reporting_period.end_date) \
            .exclude(id__in=filed_users) \
            .filter(user_data__current_employee=True) \
            .order_by('last_name', 'first_name')
        context['reporting_period'] = reporting_period
        return context


def ReportingPeriodCSVView(request, reporting_period):
    """Export a CSV of a specific reporting period"""
    response = HttpResponse(content_type='text/csv')
    disposition = 'attachment; filename="{0}.csv"'.format(reporting_period)
    response['Content-Disposition'] = disposition

    writer = csv.writer(response)
    timecard_objects = TimecardObject.objects.filter(
        timecard__reporting_period__start_date=reporting_period
    ).order_by(
        'timecard__reporting_period__start_date'
    ).select_related(
        'timecard__user',
        'timecard__reporting_period',
        'project',
    )

    writer.writerow(["Reporting Period", "Last Modified", "User", "Project",
                     "Number of Hours"])
    for timecard_object in timecard_objects:
        # skip entries if timecard not submitted yet
        if not timecard_object.timecard.submitted:
            continue

        writer.writerow(
            ["{0} - {1}".format(
                timecard_object.timecard.reporting_period.start_date,
                timecard_object.timecard.reporting_period.end_date),
             timecard_object.timecard.modified.strftime("%Y-%m-%d %H:%M:%S"),
             timecard_object.timecard.user.username, timecard_object.project,
             timecard_object.hours_spent])

    return response


class ReportingPeriodUserDetailView(DetailView):
    model = Timecard
    template_name = "hours/reporting_period_user_detail.html"

    def get_object(self):
        obj = Timecard.objects.prefetch_related(
            'timecardobjects__project',
            'timecardobjects__project__accounting_code'
        ).get(
            reporting_period__start_date=self.kwargs['reporting_period'],
            user__username=self.kwargs['username']
        )
        return obj

    def get_context_data(self, **kwargs):
        user_billable_hours = TimecardObject.objects.filter(
            timecard__reporting_period__start_date=\
                self.kwargs['reporting_period'],
            timecard__user__username=self.kwargs['username'],
            project__accounting_code__billable=True
        ).aggregate(
            (
                Sum('hours_spent')
            )
        )['hours_spent__sum']

        user_all_hours = TimecardObject.objects.filter(
            timecard__reporting_period__start_date=\
                self.kwargs['reporting_period'],
            timecard__user__username=self.kwargs['username'],
        ).aggregate(
            (
                Sum('hours_spent')
            )
        )['hours_spent__sum']

        context = super(
            ReportingPeriodUserDetailView, self).get_context_data(**kwargs)
        context['user_billable_hours'] = user_billable_hours
        context['user_all_hours'] = user_all_hours
        context['user_utilization'] = calculate_utilization(
            context['user_billable_hours'],
            context['user_all_hours']
        )
        return context
