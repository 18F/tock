from api.views import get_timecardobjects
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from hours.models import TimecardObject
from utilization.analytics import project_chart_and_table

from .models import Project


class ProjectListView(LoginRequiredMixin, ListView):
    """ View for listing all of the projects, sort projects by name """
    model = Project
    template_name = 'projects/project_list.html'

    queryset = Project.objects.all().prefetch_related('alerts').order_by('name')

    def get_context_data(self, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)
        return context


class ProjectView(LoginRequiredMixin, DetailView):
    """ View for listing the details of a specific project """
    model = Project
    template_name = 'projects/project_detail.html'

    def get_analytics(self, timecard_entries):
        """Return a dict ready for the context with a plotly chart and data table"""
        plot, table = project_chart_and_table(timecard_entries)
        return {
                "project_data": table,
                "project_plot": plot
            }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        timecard_entries = get_timecardobjects(TimecardObject.objects.filter(project=self.object))

        context['total_hours_submitted'] = timecard_entries.filter(timecard__submitted=True
        ).aggregate(Sum('hours_spent'))['hours_spent__sum'] or 0
        context['total_hours_saved'] = timecard_entries.filter(timecard__submitted=False
        ).aggregate(Sum('hours_spent'))['hours_spent__sum'] or 0
        context['total_hours_all'] = context['total_hours_submitted'] + context['total_hours_saved']

        if context['total_hours_all']:
            context.update(self.get_analytics(timecard_entries))


        return context
