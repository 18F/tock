import datetime

from django.db.models import Sum, Prefetch
from django.views.generic import ListView

from hours.models import Timecard, TimecardObject, ReportingPeriod
from employees.models import UserData

"""Functions to get date and reporting period info. Currently used for the
GroupUtilizationView. Could be used for other views, including individual
utilization views."""

def get_fy_first_day(date):
    if date.month <= 9:
        year = (date - datetime.timedelta(weeks=52)).year
    else:
        year = date.year
    fy_first_day = datetime.date(year, 10, 1)
    return fy_first_day

def get_dates(periods):
    today = datetime.date.today()
    fy_first_day = get_fy_first_day(today)
    reportingperiods = ReportingPeriod.objects.filter(
        end_date__lte=today).order_by('-start_date')[:periods]
    reportingperiods_start_date = reportingperiods[len(
        reportingperiods)-1].start_date
    reportingperiods_end_date = reportingperiods[0].end_date
    if reportingperiods_end_date <= fy_first_day:
        earliest_date = reportingperiods_end_date
    else:
        earliest_date = fy_first_day


    return reportingperiods, reportingperiods_start_date, \
        reportingperiods_end_date, fy_first_day, earliest_date


"""Currently set to last four reporting periods, could accept a form response
that allows the user or app to dynamically customize number of periods."""
recent_rps = get_dates(4)

class GroupUtilizationView(ListView):
    template_name = 'utilization/group_utilization.html'

    """Calculates utilization as hours billed divided by hours worked."""
    def calculate_utilization(self, timecardobjects):
        all_hours = timecardobjects.aggregate(Sum('hours_spent'))

        if all_hours['hours_spent__sum']:
            billable_hours = timecardobjects.filter(
                project__accounting_code__billable=True
                ).prefetch_related('project').aggregate(Sum('hours_spent'))
            if billable_hours['hours_spent__sum'] is None or 0:
                utilization = '0.00%'
            else:
                utilization = '{:.3}%'.format(
                    (billable_hours['hours_spent__sum'] / \
                        all_hours['hours_spent__sum']) * 100
                )
            return utilization
        else:
           return 'No hours submitted.'

    def get_queryset(self):
        """Gets submitted timecards limited to the reporting periods in
        question."""
        submitted_timecards = Timecard.objects.filter(
            submitted=True,
            reporting_period__start_date__gte=recent_rps[4]
        )
        billable_staff = UserData.objects.filter(
            is_billable=True,
            current_employee=True
        ).prefetch_related(
            Prefetch(
                'user__timecards',
                queryset=submitted_timecards,
                to_attr='submitted_timecards'
            )
        )

        for staffer in billable_staff:
            tos = TimecardObject.objects.filter(
                timecard__in=staffer.user.submitted_timecards
            )

            """Calculate utilization for recent reporting periods."""
            tos_recent = tos.filter(
                timecard__reporting_period__start_date__gte= \
                    recent_rps[1].strftime('%Y-%m-%d')).prefetch_related(
                        'timecard'
                    )
            staffer.recent = self.calculate_utilization(tos_recent)

            """Calculate utilization for last reporting period."""
            most_recent_rp = recent_rps[0][0]
            tos_most_recent = tos.filter(
                timecard__reporting_period=most_recent_rp
            ).prefetch_related('timecard')
            staffer.last = self.calculate_utilization(tos_most_recent)

            """Calculate utilization for fiscal year to lastest reporting
            period."""
            tos_fytd = tos.filter(
                timecard__reporting_period__start_date__gte=recent_rps[3]
            ).prefetch_related('timecard')
            staffer.fytd = self.calculate_utilization(tos_fytd)

        return billable_staff


    def get_context_data(self, **kwargs):
        context = super(GroupUtilizationView, self).get_context_data(**kwargs)
        context.update(
            {
                'unit_choices': UserData.UNIT_CHOICES,
                'through_date': recent_rps[2],
                'recent_start_date': recent_rps[1],
            }
        )
        return context
