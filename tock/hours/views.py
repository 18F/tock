import csv
import datetime
import io
from decimal import Decimal
from itertools import chain
from operator import attrgetter

# Create your views here.
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.db.models import Prefetch, Q, Sum
from django.contrib.auth.decorators import user_passes_test
from django.template.defaultfilters import pluralize

from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

from api.views import get_timecards, TimecardList, ProjectSerializer, UserDataSerializer
from api.renderers import stream_csv
from employees.models import UserData
from projects.models import AccountingCode
from tock.remote_user_auth import email_to_username
from tock.utils import PermissionMixin, IsSuperUserOrSelf

from .models import ReportingPeriod, Timecard, TimecardObject, Project
from .forms import (
    ReportingPeriodForm,
    ReportingPeriodImportForm,
    projects_as_choices,
    TimecardForm,
    TimecardFormSet,
    timecard_formset_factory
)
from utilization.utils import calculate_utilization


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
        context['completed_reporting_periods'] = self.queryset.filter(
            timecard__submitted=True,
            timecard__user=self.request.user.id
        ).distinct().order_by('-start_date')[:5]

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

def display_add_hours_error_message(request):
    error_msg = "Oops. That command was not correct and no time was added to your timecard. Try again by entering a URL with this format: tock.gov/addHours?project=231&hours=1"
    messages.add_message(
        request,
        messages.ERROR,
        error_msg
    )


def add_hours_view(request):
    project_id = request.GET['project']
    hours = Decimal(request.GET['hours'])
    r = ReportingPeriod.objects.latest()

    try:
        proj = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        display_add_hours_error_message(request)
        return redirect(reverse('reportingperiod:UpdateTimesheet', args=[r]))

    tc, created = Timecard.objects.get_or_create(
        reporting_period_id=r.id,
        user_id=request.user.id)

    if created:
        tc.save()

    tco, created = TimecardObject.objects.get_or_create(
        timecard_id=tc.id,
        project_id=proj.id)

    if tco.hours_spent is None:
        tco.hours_spent = 0
        display_add_hours_error_message(request)
        return redirect(reverse('reportingperiod:UpdateTimesheet', args=[r]))

    updated_hours = tco.hours_spent + hours
    updated_hours = max(0, updated_hours)

    tco.hours_spent = updated_hours
    tco.save()

    if hours > 0:
        plural_hours = pluralize(hours, 'hour,hours')
        has = pluralize(hours, 'has,have')
        undo_query = "?hours=-%s&project=%s" % (hours, proj.id)
        undo_url = reverse('AddHours') + undo_query
        undo_tag = "<a href=\"%s\">Undo</a>" % (undo_url)
        msg = "%s %s %s been added to %s. %s" % (hours, plural_hours, has,
                proj.name, undo_tag)
    else:
        plural_hours = pluralize(-hours, 'hour,hours')
        has = pluralize(-hours, 'has,have')
        msg = "%s %s %s been removed from %s." % (-hours, plural_hours, has,
                proj.name)

    messages.add_message(request, messages.INFO, msg)
    return redirect(reverse('reportingperiod:UpdateTimesheet', args=[r]))

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
            last_tc = self.last_timecard()
            if last_tc:
                return self.prefilled_formset(last_tc)

        return TimecardFormSet(instance=self.object)

    def last_timecard(self):
        return Timecard.objects.filter(
            reporting_period__start_date__lt=self.report_date,
            user_id=self.request.user.id,
            submitted=True,
        ).order_by(
            '-reporting_period__start_date',
        ).first()

    def prefilled_formset(self, timecard):
        project_ids = set(
            tco.project_id for tco in
            timecard.timecardobjects.all()
        )
        extra = len(project_ids) + 1
        formset = timecard_formset_factory(extra=extra)
        return formset(initial=[
            {'hours_spent': None, 'project': pid}
            for pid in project_ids
        ])

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
