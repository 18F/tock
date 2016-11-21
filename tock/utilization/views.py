import datetime

from django.db.models import Sum, Prefetch
from django.views.generic import ListView
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from hours.models import Timecard, TimecardObject, ReportingPeriod
from employees.models import UserData

from .utils import get_fy_first_day, get_dates, calculate_utilization

class GroupUtilizationView(ListView):
    template_name = 'utilization/group_utilization.html'

    def get_queryset(self):
        """Gets submitted timecards limited to the reporting periods in
        question."""

        """Although recent_rps is set to last four reporting periods, could
        accept a form response that allows the user or app to dynamically
        customize number of periods to include in the queryset."""

        available_periods = ReportingPeriod.objects.count()
        requested_periods = 4

        if available_periods >= requested_periods:
            recent_rps = get_dates(requested_periods)
        else:
            recent_rps = get_dates(available_periods)

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
                'timecard__user',
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


            staffer.fytd = calculate_utilization(
                fytd_billable_hours['hours_spent__sum'],
                fytd_all_hours['hours_spent__sum']
            )
            staffer.fytd_all_hours_total = fytd_all_hours['hours_spent__sum']
            if fytd_billable_hours['hours_spent__sum']:
                staffer.fytd_billable_hours_total = fytd_billable_hours['hours_spent__sum']
            else:
                staffer.fytd_billable_hours_total = 0.0

            staffer.recent = calculate_utilization(
                recent_billable_hours['hours_spent__sum'],
                recent_all_hours['hours_spent__sum']
            )
            staffer.recent_all_hours_total = recent_all_hours['hours_spent__sum']
            if recent_billable_hours['hours_spent__sum']:
                staffer.recent_billable_hours_total = recent_billable_hours['hours_spent__sum']
            else:
                staffer.recent_billable_hours_total = 0.0


            staffer.last = calculate_utilization(
                last_billable_hours['hours_spent__sum'],
                last_all_hours['hours_spent__sum']
            )
            staffer.last_all_hours_total = last_all_hours['hours_spent__sum']
            if last_billable_hours['hours_spent__sum']:
                staffer.last_billable_hours_total = last_billable_hours['hours_spent__sum']
            else:
                staffer.last_billable_hours_total = 0.0



            print()
            staffer.last_url = reverse(
                'reports:ReportingPeriodUserDetailView',
                kwargs={
                        'username':staffer,
                        'reporting_period': recent_rps[4]
                }
            )

        return billable_staff

    def get_context_data(self, **kwargs):
        context = super(GroupUtilizationView, self).get_context_data(**kwargs)

        available_periods = ReportingPeriod.objects.count()
        requested_periods = 4

        if available_periods >= requested_periods:
            recent_rps = get_dates(requested_periods)
        else:
            recent_rps = get_dates(available_periods)

        context.update(
            {
                'unit_choices': UserData.UNIT_CHOICES,
                'through_date': recent_rps[0],
                'recent_start_date': recent_rps[1],
            }
        )
        return context
