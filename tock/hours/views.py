from django.shortcuts import render

# Create your views here.
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from tock.utils import LoginRequiredMixin

from .models import ReportingPeriod, Timecard, TimecardObject
from .forms import TimecardForm, TimecardFormSet

import datetime

def home(request):
   context = RequestContext(request,
                           {'request': request,
                            'user': 'hello'})
   return render_to_response('base.html',
                             context_instance=context)

class ReportingPeriodListView(ListView):
    context_object_name = "incomplete_reporting_periods"
    queryset = ReportingPeriod.objects.all()
    template_name = "hours/reporting_period_list.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ReportingPeriodListView, self).get_context_data(**kwargs)
        # Add in the current user
        context['completed_reporting_periods'] = ReportingPeriod.objects.filter(timecard__user=self.request.user)
        context['uncompleted_reporting_periods'] = ReportingPeriod.objects.all().exclude(timecard__user=self.request.user)
        context['user'] = self.request.user
        context['email'] = self.request.user.username
        return context

class TimecardView(UpdateView):
    form_class = TimecardForm
    template_name = 'hours/timecard_form.html'

    def get_object(self, queryset=None):
        r = ReportingPeriod.objects.get(start_date=datetime.datetime.strptime(self.kwargs['reporting_period'], "%Y-%m-%d").date())
        obj, created = Timecard.objects.get_or_create(reporting_period_id=r.id, user_id=self.request.user.id)
        return obj

    def get_context_data(self, **kwargs):
        context = super(TimecardView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = TimecardFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = TimecardFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.reporting_period = ReportingPeriod.objects.get(start_date=self.kwargs['reporting_period'])
            self.object.save()
            formset.instance = self.object
            formset.save()
            return super(UpdateView, self).form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse("ListReportingPeriods")