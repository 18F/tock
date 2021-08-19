from api.views import get_timecardobjects
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
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


class ProjectEngagementView(LoginRequiredMixin, ListView):
    """ View for listing the details of a specific project """
    model = Project
    template_name = 'projects/project_engagement.html'

    def get_queryset(self):
        """The projects here are active with engagement management lines."""
        em_projects = Project.objects.filter(active=True,
                name__endswith="Engagement Management")
        # get the non-EM projects and try to match them up
        other_projects = Project.objects.filter(active=True).filter(~Q(name__endswith="Engagement Management"))
        matched_projects = []
        for em_project in em_projects:
            # match on the name of the engagement, this may not always work
            matches = [p for p in other_projects if em_project.name.startswith(p.name)]
            if matches:
                matched_projects.append({"project": matches[0], "em_project": em_project})  # use the first match, probably won't be any others

        # enrich with additional information
        for item in matched_projects:
            item["em_hours"] = item["em_project"].timecardobject_set.aggregate(z=Sum("hours_spent"))["z"]
            item["hours"] = item["project"].timecardobject_set.aggregate(z=Sum("hours_spent"))["z"]
            if item["em_hours"] and item["hours"]:
                item["ratio"] = item["em_hours"] / item["hours"]
            else:
                item["ratio"] = 0.0

        # sort by descending ratio
        return sorted(matched_projects, key=lambda item: item["ratio"], reverse=True)
