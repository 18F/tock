from django.shortcuts import render

# Create your views here.
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.decorators import login_required

from tock.utils import LoginRequiredMixin

from .models import Week, Timecard, TimecardObject
from .forms import TimecardForm, TimecardFormSet

def home(request):
   context = RequestContext(request,
                           {'request': request,
                            'user': 'hello'})
   return render_to_response('base.html',
                             context_instance=context)

class WeekListView(ListView):
    context_object_name = "week_list"
    queryset = Week.objects.all()
    template_name = "hours/week_list.html"


class TimecardCreateView(CreateView):
    form_class = TimecardForm
    template_name = 'hours/timecard_form.html'

    def get_context_data(self, **kwargs):
        context = super(TimecardCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = TimecardFormSet(self.request.POST)
        else:
            context['formset'] = TimecardFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save(commit=False)
            self.object.user = "sean.herron@gsa.gov"
            self.object.week = Week.objects.get(start_date=self.kwargs['week'])
            self.object.save()
            formset.instance = self.object
            formset.save()
            return super(CreateView, self).form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class TimecardUpdateView(UpdateView):
    form_class = TimecardForm
    template_name = 'hours/timecard_form.html'

    def get_object(self, queryset=None):
        obj = Timecard.objects.get(week__start_date=self.kwargs['week'], user="sean.herron@gsa.gov")
        return obj

    def get_context_data(self, **kwargs):
        context = super(TimecardUpdateView, self).get_context_data(**kwargs)
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
            self.object.user = "sean.herron@gsa.gov"
            self.object.week = Week.objects.get(start_date=self.kwargs['week'])
            self.object.save()
            formset.instance = self.object
            formset.save()
            return super(UpdateView, self).form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))