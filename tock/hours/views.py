import csv
import io
import datetime
from itertools import chain
from operator import itemgetter, attrgetter

# Create your views here.
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template.context import RequestContext
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.exceptions import ValidationError

from tock.utils import LoginRequiredMixin
from tock.remote_user_auth import email_to_username

from .utils import number_of_hours
from .models import ReportingPeriod, Timecard, TimecardObject, Project
from .forms import TimecardForm, TimecardFormSet, ReportingPeriodForm, ReportingPeriodImportForm


class ReportingPeriodListView(ListView):
    context_object_name = "incomplete_reporting_periods"
    queryset = ReportingPeriod.objects.all()
    template_name = "hours/reporting_period_list.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(
            ReportingPeriodListView, self).get_context_data(**kwargs)
        # Add in the current user
        context['completed_reporting_periods'] = self.queryset.filter(
            timecard__time_spent__isnull=False,
            timecard__user=self.request.user).distinct().order_by('-start_date')[:5]

        try:
            unstarted_reporting_periods = self.queryset.exclude(
                timecard__user=self.request.user).exclude(end_date__lte=self.request.user.user_data.start_date)
            unfinished_reporting_periods = self.queryset.filter(
                timecard__time_spent__isnull=True,
                timecard__user=self.request.user).exclude(end_date__lte=self.request.user.user_data.start_date)
        except ValueError:
            unstarted_reporting_periods = self.queryset.exclude(
                timecard__user=self.request.user)
            unfinished_reporting_periods = self.queryset.filter(
                timecard__time_spent__isnull=True,
                timecard__user=self.request.user)

        context['uncompleted_reporting_periods'] = sorted(list(
            chain(unstarted_reporting_periods, unfinished_reporting_periods)), key=attrgetter('start_date'))
        return context


class ReportingPeriodCreateView(CreateView):
    form_class = ReportingPeriodForm
    template_name = 'hours/reporting_period_form.html'

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_superuser:
            return super(ReportingPeriodCreateView, self).dispatch(*args, **kwargs)
        else:
            raise PermissionDenied

    def get_success_url(self):
        return reverse("ListReportingPeriods")


class ReportingPeriodBulkImportView(FormView):
    template_name = 'hours/reporting_period_import.html'
    form_class = ReportingPeriodImportForm

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_superuser:
            return super(ReportingPeriodBulkImportView, self).dispatch(*args, **kwargs)
        else:
            raise PermissionDenied

    def form_valid(self, form):
        if form.is_valid():
            reporting_period = form.cleaned_data['reporting_period']
            line_items = io.StringIO(
                self.request.FILES['line_items'].read().decode('utf-8'), newline=None)

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
                    raise ValidationError('Project %s (Code %s) Does Not Exist' % (
                        line_item['Tock Proj. Name'], line_item['Tock Code']))

                try:
                    TimecardObject.objects.get(
                        timecard=timecard, project=project, hours_spent=line_item['Hours Logged'])
                except TimecardObject.DoesNotExist:
                    TimecardObject.objects.create(
                        timecard=timecard, project=project, hours_spent=line_item['Hours Logged'])

        return super(ReportingPeriodBulkImportView, self).form_valid(form)

    def get_success_url(self):
        return reverse("ListReportingPeriods")


class TimecardView(UpdateView):
    form_class = TimecardForm
    template_name = 'hours/timecard_form.html'

    def get_object(self, queryset=None):
        r = ReportingPeriod.objects.get(start_date=datetime.datetime.strptime(
            self.kwargs['reporting_period'], "%Y-%m-%d").date())
        obj, created = Timecard.objects.get_or_create(reporting_period_id=r.id,
                                                      user_id=self.request.user.id)
        return obj

    def get_context_data(self, **kwargs):
        context = super(TimecardView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = TimecardFormSet(self.request.POST,
                                                 instance=self.object)
        else:
            context['formset'] = TimecardFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.reporting_period = ReportingPeriod.objects.get(
                start_date=self.kwargs['reporting_period'])
            self.object.save()
            formset.instance = self.object
            formset.save()
            return super(UpdateView, self).form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse("ListReportingPeriods")


class ReportsList(ListView):

    """Show a list of all Reporting Periods to navigate to various reports"""
    template_name = "hours/reports_list.html"

    def get_queryset(self, queryset=None):
        query = ReportingPeriod.objects.all()
        fiscal_years = {}
        for reporting_period in query:
            if str(reporting_period.get_fiscal_year()) in fiscal_years:
                fiscal_years[str(
                    reporting_period.get_fiscal_year())].append(reporting_period)
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
        return Timecard.objects.filter(reporting_period__start_date=datetime.datetime.strptime(self.kwargs['reporting_period'],
                                                                                               "%Y-%m-%d").date(), time_spent__isnull=False).distinct().order_by('user__last_name', 'user__first_name')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(
            ReportingPeriodDetailView, self).get_context_data(**kwargs)
        reporting_period = ReportingPeriod.objects.get(start_date=datetime.datetime.strptime(self.kwargs['reporting_period'],
                                                                                             "%Y-%m-%d").date())
        filed_users = list(Timecard.objects.filter(reporting_period=reporting_period,
                                                   time_spent__isnull=False).distinct().all().values_list('user__id', flat=True))
        context['users_without_filed_timecards'] = get_user_model().objects.exclude(
            user_data__start_date__gte=reporting_period.end_date).exclude(id__in=filed_users).order_by('last_name', 'first_name')
        context['reporting_period'] = reporting_period
        return context

def ReportingPeriodCSVView(request, reporting_period):
    """Export a CSV of a specific reporting period"""
    response = HttpResponse(content_type='text/csv')
    response[
        'Content-Disposition'] = 'attachment; filename="%s.csv"' % reporting_period

    writer = csv.writer(response)
    timecard_objects = TimecardObject.objects.filter(
        timecard__reporting_period__start_date=reporting_period)

    writer.writerow(["Reporting Period", "Last Modified", "User", "Project",
                     "Number of Hours"])
    for timecard_object in timecard_objects:
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
            user__username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ReportingPeriodUserDetailView,
                        self).get_context_data(**kwargs)
        return context
