from collections import defaultdict

from django.db.models import Sum
from django.views.generic import ListView
from django.views.generic.detail import DetailView

from hours.models import TimecardObject
from .models import Project
from tock.utils import PermissionMixin


class ProjectListView(PermissionMixin, ListView):
    """ View for listing all of the projects, sort projects by name """
    model = Project
    template_name = 'projects/project_list.html'

    queryset = Project.objects.all().prefetch_related('alerts').order_by('name')

    def get_context_data(self, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)
        return context


class ProjectView(PermissionMixin, DetailView):
    """ View for listing the details of a specific project """
    model = Project
    template_name = 'projects/project_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table'] = project_timeline(kwargs['object'])
        context['total_hours_submitted'] = TimecardObject.objects.filter(
            project=kwargs['object'].id, timecard__submitted=True
        ).aggregate(Sum('hours_spent'))['hours_spent__sum'] or 0
        context['total_hours_saved'] = TimecardObject.objects.filter(
            project=kwargs['object'].id, timecard__submitted=False
        ).aggregate(Sum('hours_spent'))['hours_spent__sum'] or 0
        context['total_hours_all'] = context['total_hours_submitted'] + context['total_hours_saved']
        return context


def project_timeline(project, period_limit=5):
    """
    Gather hours spent per user per reporting period for the specified
    project, defaulted to the five most recent time periods. Returns hours
    per user per period, plus an ordered list of periods.
    """
    groups, periods = defaultdict(dict), []

    # fetch timecard objs, sorted by report period date
    timecards = TimecardObject.objects.filter(
        project=project
    ).order_by(
        '-timecard__reporting_period__start_date'
    ).select_related(
        'timecard__user',
        'timecard__reporting_period',
    )

    for t in timecards:
        tc = t.timecard
        report_date = tc.reporting_period.start_date

        # skip if timecard not submitted yet
        if not tc.submitted:
            continue

        # add report date to period array if not present
        # if period limit set, stop after limit reached
        if report_date not in periods:
            if len(periods) == period_limit:
                break
            periods.append(report_date)

        groups[tc.user][report_date] = float(t.hours_spent)

    return {
        'groups': dict(groups),
        'periods': sorted(periods),
    }
