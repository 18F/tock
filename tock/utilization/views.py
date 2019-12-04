from django.core.exceptions import PermissionDenied
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.views.generic import ListView

from hours.models import TimecardObject, ReportingPeriod
from employees.models import UserData

from tock.utils import PermissionMixin
from .utils import get_dates, calculate_utilization

class GroupUtilizationView(PermissionMixin, ListView):
    template_name = 'utilization/group_utilization.html'
    requested_periods = 4

    def dispatch(self, *args, **kwargs):
        """
        Resolve recent reporting periods.

        Although recent_rps is set to the last four reporting periods,
        we could accept a form response that allows the user or app to
        dynamically customize number of periods to include in the queryset.

        Also, if they're not staff, we're going to go ahead and bounce
        them to 403 so we don't make all these queries.
        """
        if not self.request.user.is_authenticated:
            return self.handle_no_permission()
        if not self.request.user.is_staff:
            raise PermissionDenied
        self.available_periods = ReportingPeriod.objects.count()

        if self.available_periods >= self.requested_periods:
            self.recent_rps = get_dates(self.requested_periods)
        else:
            self.recent_rps = get_dates(self.available_periods)
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        """
        Gets submitted timecards for billable staff
        limited to the reporting periods in question.
        """
        # Start stubbing a dict for our units, using a quick list comprehension
        units = [{
            'id': choice[0],
            'name': choice[1],
            'slug': slugify(choice[1])
         } for choice in UserData.UNIT_CHOICES]
        # now we'll start building out that dict further,
        # starting with the staff for each unit
        for unit in units:
            billable_staff = UserData.objects.filter(
                is_billable=True,
                current_employee=True,
                unit = unit['id']
            ).prefetch_related('user')

            for staffer in billable_staff:
                """
                Create smallest possible TimecardObject queryset based on the
                earliest_date value returned by get_dates(). Also prefetches the
                related user and accounting code for later use.

                We're casting this to values() because we need very little data,
                it's faster, and we can work with it in pure python so we avoid
                additional queries hitting the database.
                """
                user_timecards = TimecardObject.objects.filter(
                    timecard__submitted=True,
                    timecard__user=staffer.user,
                    timecard__reporting_period__start_date__gte=self.recent_rps[3]
                ).select_related(
                    'timecard__reporting_period',
                    'project__accounting_code__billable'
                ).values(
                    'id',
                    'hours_spent',
                    'timecard__reporting_period',
                    'timecard__reporting_period__start_date',
                    'project__accounting_code__billable'
                )
                """
                We also need to know the billable cards, but
                we only need the IDs to boil down each reporting period QS
                and find the intersection below.
                """
                user_billable_timecard_ids = user_timecards.filter(
                    project__accounting_code__billable=True
                ).values_list('id', flat=True)

                """
                Filter the timecard queryset to only look for cards that are
                related to reporting periods within the current fiscal year.

                This operation is unnecessary except at the beginning of the
                fiscal year.
                """
                fytd_hours = []
                for card in user_timecards:
                    if card['timecard__reporting_period__start_date'] >= self.recent_rps[2]:
                        fytd_hours.append(card['hours_spent'])
                fytd_hours = sum(fytd_hours)

                fytd_billable = []
                for card in user_timecards:
                    if card['timecard__reporting_period__start_date'] >= self.recent_rps[2] \
                    and card['id'] in user_billable_timecard_ids:
                        fytd_billable.append(card['hours_spent'])
                fytd_billable = sum(fytd_billable)

                staffer.fytd = calculate_utilization(fytd_billable, fytd_hours)
                staffer.fytd_all_hours_total: fytd_hours
                staffer.fytd_billable_hours = fytd_billable if fytd_billable else 0.0

                """
                Get hours for reporting periods within the last n reporting
                periods, where n is the argument passed to the get_dates()
                function.
                """
                recent_hours = []
                for card in user_timecards:
                    if card['timecard__reporting_period__start_date'] >= self.recent_rps[1]:
                        recent_hours.append(card['hours_spent'])
                recent_hours = sum(recent_hours)

                recent_billable = []
                for card in user_timecards:
                    if card['timecard__reporting_period__start_date'] >= self.recent_rps[1] \
                    and card['id'] in user_billable_timecard_ids:
                        recent_billable.append(card['hours_spent'])
                recent_billable = sum(recent_billable)

                staffer.recent = calculate_utilization(recent_billable, recent_hours)
                staffer.recent_all_hours_total = recent_hours
                staffer.recent_billable_hours_total = recent_billable if recent_billable else 0.0
                """
                Get hours from the latest reporting period
                """
                last_hours = []
                for card in user_timecards:
                    if card['timecard__reporting_period__start_date'] >= self.recent_rps[0]:
                        last_hours.append(card['hours_spent'])
                last_hours = sum(last_hours)

                last_billable = []
                for card in user_timecards:
                    if card['timecard__reporting_period__start_date'] >= self.recent_rps[0] \
                    and card['id'] in user_billable_timecard_ids:
                        last_billable.append(card['hours_spent'])
                last_billable = sum(last_billable)

                staffer.last = calculate_utilization(last_billable, last_hours)
                staffer.last_all_hours_total = last_hours
                staffer.last_billable_hours_total = last_billable if last_billable else 0.0

                staffer.last_url = reverse(
                    'reports:ReportingPeriodUserDetailView',
                    kwargs={
                            'username':staffer.user,
                            'reporting_period': self.recent_rps[4]
                    }
                )

            unit['billable_staff'] = billable_staff

            last_total_hours = sum(TimecardObject.objects.filter(
                timecard__reporting_period__start_date=self.recent_rps[4],
                timecard__submitted=True,
                timecard__user__user_data__unit=unit['id'],
                ).values_list('hours_spent', flat=True)
            )
            last_billable_hours = sum(TimecardObject.objects.filter(
                timecard__submitted=True,
                timecard__reporting_period__start_date=self.recent_rps[4],
                timecard__user__user_data__unit=unit['id'],
                project__accounting_code__billable=True
                ).values_list('hours_spent', flat=True)
            )
            # Query and calculate last in RP hours.
            recent_total_hours = sum(TimecardObject.objects.filter(
                timecard__submitted=True,
                timecard__reporting_period__start_date__gte=self.recent_rps[1],
                timecard__user__user_data__unit=unit['id']
                ).values_list('hours_spent', flat=True)
            )
            recent_billable_hours = sum(
                TimecardObject.objects.filter(
                    timecard__submitted=True,
                    timecard__reporting_period__start_date__gte=self.recent_rps[1],
                    timecard__user__user_data__unit=unit['id'],
                    project__accounting_code__billable=True
                ).values_list('hours_spent', flat=True)
            )
            # Query and calculate all RP hours for FY to date.
            fytd_total_hours = sum(
                TimecardObject.objects.filter(
                    timecard__submitted=True,
                    timecard__reporting_period__start_date__gte=self.recent_rps[2],
                    timecard__user__user_data__unit=unit['id'],
                ).values_list('hours_spent', flat=True)
            )
            fytd_billable_hours = sum(TimecardObject.objects.filter(
                timecard__submitted=True,
                timecard__reporting_period__start_date__gte=self.recent_rps[2],
                timecard__user__user_data__unit=unit['id'],
                project__accounting_code__billable=True
                ).values_list('hours_spent', flat=True)
            )

            unit.update({
                'last': {
                    'unit_name': unit['name'],
                    'billable_hours': last_billable_hours,
                    'total_hours': last_total_hours,
                    'utilization': calculate_utilization(
                        last_billable_hours,
                        last_total_hours
                    )
                },
                'recent': {
                    'unit_name': unit['name'],
                    'billable_hours': recent_billable_hours,
                    'total_hours': recent_total_hours,
                    'utilization': calculate_utilization(
                        recent_billable_hours,
                        recent_total_hours
                    )
                },
                'fytd': {
                    'unit_name': unit['name'],
                    'billable_hours': fytd_billable_hours,
                    'total_hours': fytd_total_hours,
                    'utilization': calculate_utilization(
                        fytd_billable_hours,
                        fytd_total_hours
                    )
                }
            })

        return units

    def get_context_data(self, **kwargs):
        context = super(GroupUtilizationView, self).get_context_data(**kwargs)
        context.update(
            {
                'through_date': self.recent_rps[0],
                'recent_start_date': self.recent_rps[1],
            }
        )
        return context
