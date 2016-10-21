import datetime

from django.db.models import Sum, Prefetch
from django.views.generic import ListView
from django.contrib.auth.models import User

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

    # Grab last n reporting periods with an end date that is less than today.
    reportingperiods = ReportingPeriod.objects.filter(
        end_date__lt=today).order_by('-start_date')[:periods]

    # Grab end date of last reporting period.
    reportingperiods_end_date = reportingperiods[0].end_date

    # Grab start date of first reporting period.
    reportingperiods_start_date = reportingperiods[periods - 1].start_date

    # Set the earliest date from which TimecardObjects need to be queried.
    if reportingperiods_start_date <= fy_first_day:
        earliest_date = reportingperiods_start_date
    else:
        earliest_date = fy_first_day

    return reportingperiods_end_date, reportingperiods_start_date, \
        fy_first_day, earliest_date


"""Currently set to last four reporting periods, could accept a form response
that allows the user or app to dynamically customize number of periods."""
recent_rps = get_dates(4)

class GroupUtilizationView(ListView):
    template_name = 'utilization/group_utilization.html'

    """Calculates utilization as hours billed divided by hours worked."""
    def calculate_utilization(self, billable_hours, all_hours):
        if all_hours is (None or 0):
            return 'No hours submitted.'
        else:
            if billable_hours is None:
                return '0.00%'
            else:
                return '{:.3}%'.format((billable_hours / all_hours * 100))

    def get_queryset(self):
        """Gets submitted timecards limited to the reporting periods in
        question."""

        billable_staff = User.objects.filter(
            user_data__is_billable=True,
            user_data__current_employee=True
        ).prefetch_related('user_data')

        for staffer in billable_staff:
            staffer.unit = staffer.user_data.unit

            """Create smallest possible TimecardObject queryset based on the
            earliest_date value returned by get_dates(). Also prefetches the
            related user and accounting code for later use."""
            max_tos = TimecardObject.objects.filter(
                timecard__user=staffer,
                submitted=True,
                timecard__reporting_period__start_date__gte=recent_rps[3]
            ).prefetch_related(
                'timecard__user'
            ).prefetch_related(
                'project__accounting_code'
            )

            """Filters the max_tos queryset to only look for TimecardObjects
            that are related to reporting periods within the current fiscal
            year. This operation is unnecessary except at the beginning of the
            fiscal year."""
            fytd_tos = max_tos.filter(
                timecard__reporting_period__start_date__gte=recent_rps[2])

            """Calcuates the billable hours decimal value in the queryset."""
            fytd_billable_hours = fytd_tos.filter(
                project__accounting_code__billable=True
            ).aggregate(
                Sum('hours_spent'
                )
            )
            #print('ytd bill  {}'.format(fytd_billable_hours))

            """Calcuates the all hours decimal value in the queryset."""
            fytd_all_hours = fytd_tos.aggregate(
                Sum('hours_spent'
                )
            )
            #print('ytd all  {}'.format(fytd_all_hours))

            """Filters the fytd_tos queryset to only look for TimecardObjects
            that are related to reporting periods within the last n reporting
            periods, where n is the argument passed to the get_dates()
            function."""

            recent_tos = max_tos.filter(
                timecard__reporting_period__start_date__gte=recent_rps[1]
            )

            """Calcuates the billable hours decimal value in the queryset."""
            recent_billable_hours = recent_tos.filter(
                project__accounting_code__billable=True
            ).aggregate(
                Sum('hours_spent'
                )
            )
            #print('recent bill  {}'.format(recent_billable_hours))

            """Calcuates the all hours decimal value in the queryset."""
            recent_all_hours = recent_tos.aggregate(
                Sum('hours_spent'
                )
            )
            #print('recent all  {}'.format(recent_all_hours))

            """Filters the recent_tos queryset to only look for TimecardObjects
            that are related to reporting periods within the last 1 reporting
            period.
            """
            last_tos = recent_tos.filter(
                timecard__reporting_period__end_date=recent_rps[0]
            )

            """Calcuates the billable hours decimal value in the queryset."""
            last_billable_hours = last_tos.filter(
                project__accounting_code__billable=True
            ).aggregate(
                Sum('hours_spent'
                )
            )
            #print('last bill  {}'.format(last_billable_hours))

            """Calcuates the all hours decimal value in the queryset."""
            last_all_hours = last_tos.aggregate(
                Sum('hours_spent'
                )
            )
            #print('last all  {}'.format(last_all_hours))


            staffer.fytd = self.calculate_utilization(
                fytd_billable_hours['hours_spent__sum'],
                fytd_all_hours['hours_spent__sum']
            )

            staffer.recent = self.calculate_utilization(
                recent_billable_hours['hours_spent__sum'],
                recent_all_hours['hours_spent__sum']
            )

            staffer.last = self.calculate_utilization(
                last_billable_hours['hours_spent__sum'],
                last_all_hours['hours_spent__sum']
            )

        return billable_staff

    def get_context_data(self, **kwargs):
        context = super(GroupUtilizationView, self).get_context_data(**kwargs)
        context.update(
            {
                'unit_choices': UserData.UNIT_CHOICES,
                'through_date': recent_rps[0],
                'recent_start_date': recent_rps[1],
            }
        )
        return context
