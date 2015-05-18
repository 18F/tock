import csv
import datetime
from itertools import chain
from operator import itemgetter, attrgetter

# Create your views here.
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template.context import RequestContext
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db.models import Q

from tock.utils import LoginRequiredMixin

from .utils import number_of_hours
from .models import ReportingPeriod, Timecard, TimecardObject
from .forms import TimecardForm, TimecardFormSet, ReportingPeriodForm

class ReportingPeriodListView(ListView):
  context_object_name = "incomplete_reporting_periods"
  queryset = ReportingPeriod.objects.all()
  template_name = "hours/reporting_period_list.html"

  def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
    context = super(ReportingPeriodListView, self).get_context_data(**kwargs)
    # Add in the current user
    context['completed_reporting_periods'] = self.queryset.filter(
        timecard__time_spent__isnull=False,
        timecard__user=self.request.user).distinct().order_by('-start_date')[:5]
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


class ReportingPeriodDetailView(DetailView):
  model = ReportingPeriod
  template_name = "hours/reporting_period_detail.html"

  def get_object(self):
    return get_object_or_404(
        ReportingPeriod,
        start_date=datetime.datetime.strptime(self.kwargs['reporting_period'],
                                              "%Y-%m-%d").date())

  def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
    context = super(ReportingPeriodDetailView, self).get_context_data(**kwargs)
    context['users'] = User.objects.all()
    return context


def ReportingPeriodCSVView(request, reporting_period):
  """Export a CSV of a specific reporting period"""
  response = HttpResponse(content_type='text/csv')
  response['Content-Disposition'] = 'attachment; filename="%s.csv"' % reporting_period

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
         timecard_object.timecard.user, timecard_object.project,
         timecard_object.hours_spent])

  return response


class ReportingPeriodUserDetailView(DetailView):
  model = Timecard
  template_name = "hours/reporting_period_user_detail.html"

  def get_object(self):
    return get_object_or_404(
        Timecard,
        reporting_period__start_date=self.kwargs['reporting_period'],
        user__username=self.kwargs['user'])

  def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
    context = super(ReportingPeriodUserDetailView,
                    self).get_context_data(**kwargs)
    return context
