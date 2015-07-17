import itertools

from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.db.models.loading import get_model

from .models import Project


class ProjectListView(ListView):
    """ View for listing all of the projects, sort projects by name """
    model = Project
    template_name = 'projects/project_list.html'

    queryset = Project.objects.all().order_by('name')

    def get_context_data(self, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)
        return context


class ProjectView(DetailView):
    """ View for listing the details of a specific project """
    model = Project
    template_name = 'projects/project_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectView, self).get_context_data(**kwargs)
        context['table'] = project_timeline(kwargs['object'])
        return context


def project_timeline(project):
    """Gather hours spent per user per reporting period for the specified
    project. Returns hours per user per period, plus an ordered list of
    relevant periods.
    """
    TimecardObject = get_model('hours.TimecardObject')
    timecards = TimecardObject.objects.filter(
        project=project,
    ).order_by(
        'timecard__user__pk',
        '-timecard__reporting_period__start_date',
    ).select_related(
        'timecard__user',
        'timecard__reporting_period',
    ).all()
    groups = {}
    periods = set()
    for user, rows in itertools.groupby(timecards, lambda row: row.timecard.user):
        groups[user] = {
            row.timecard.reporting_period.start_date: row.hours_spent
            for row in rows
        }
        periods.update(groups[user].keys())
    return {
        'groups': groups,
        'periods': periods,
    }
