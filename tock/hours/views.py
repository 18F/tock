import csv
import datetime
import io
from itertools import chain
from operator import attrgetter

# Create your views here.
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.db.models import Prefetch, Q

from rest_framework.permissions import IsAuthenticated

from tock.remote_user_auth import email_to_username
from tock.utils import PermissionMixin, IsSuperUserOrSelf
from .models import ReportingPeriod, Timecard, TimecardObject, Project
from projects.models import AccountingCode
from .forms import (
    ReportingPeriodForm, ReportingPeriodImportForm, projects_as_choices,
    TimecardForm, TimecardFormSet, timecard_formset_factory
)


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

        if self.object.timecardobject_set.count() == 0:
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
            timecard.timecardobject_set.all()
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
        'timecard__submitted',
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
             timecard_object.timecard.user.email, timecard_object.project,
             timecard_object.hours_spent])

    return response


class ReportingPeriodUserDetailView(DetailView):
    model = Timecard
    template_name = "hours/reporting_period_user_detail.html"

    def get_object(self):
        return get_object_or_404(
            Timecard,
            reporting_period__start_date=self.kwargs['reporting_period'],
            user__username=self.kwargs['username']
        )
