import datetime

from django.db.models import Sum
from django.views.generic import ListView

from hours.models import TimecardObject, ReportingPeriod

# from django.contrib.auth.models import User
# from django.core.urlresolvers import reverse
# from django.shortcuts import get_object_or_404

class GroupUtilizationView(ListView):
    template_name = 'utilization/group_utilization.html'

    def calculate_utilization(timecardobjects):
        all_hours = timecardobjects.aggregate(Sum('hours_spent'))
        if all_hours:
            billable_hours = timecardobjects.filter(
                project__accounting_code__billable=True
                ).aggregate(Sum('hours_spent'))
            if billable_hours is None:
                billable_hours = 0
                utilization = '0%'
            else:
                utilization = '{:.3}%'.format((billable_hours / all_hours)*100)
            return utilization
        else:
           return 'No hours submitted.' 

    # Determine the earliest date from which we want time cards.

    def get_fy_first_day(date):
        if date.month <= 9:
            year = (date - datetime.timedelta(weeks=52)).year
        else:
            year = date.year
        target = datetime.date(year, 10, 1)

        return target


    #pull the four most recent reporting periods
    def get_recent_rps():

        today = datetime.date.today()
        fy_first_day = get_fy_first_day(today)

        recent_rps = ReportingPeriod.objects.filter(
            end_date__lte=today).order_by('-start_date')[:4]
        most_recent_rp = recent_rps[0]
        recent_rps_start_date = recent_rps[len(recent_rps)-1].start_date
        recent_rps_end_date = most_recent_rp.end_date

        if recent_rps_end_date <= fy_first_day:
            earliest_date = recent_rps_start_date
        else:
            earliest_date = fy_first_day
        return recent_rps, recent_rps_start_date, recent_rps_end_date, fy_first_day


    def get_queryset():

        recent_rps = get_recent_rps()

        submitted_timecards = Timecard.objects.filter(submitted=True)

        billable_staff = UserData.objects.filter(
            is_billable=True,
            current_employee=True
            ).prefetch_related(
                Prefetch('user__timecards',
                          queryset=submitted_timecards,
                          to_attr='timecards'),
                Prefetch("timecards__timecardobjects",
                          to_attr="timecardobjects")
            )

        for staffer in billable_staff:

            tos = staffer.timecardobjects

            # calculating utilization for the four most recent reporting periods
            tos_recent = tos.filter(
                reporting_period__start_date__gte= \
                recent_rps[1].strftime('%Y-%m-%d'))

            staffer.last_four = calculate_utilization(tos_recent)

            # filter timecard objects by most recent reporting period only
            most_recent_rp = recent_rps[0][0]
            tos_most_recent = tos.filter(
                reporting_period=most_recent_rp)
            staffer.last = calculate_utilization(tos_most_recent)

            # filter timecard objects by fiscal year to date
            tos_fytd = tos.filter(
                timecard__reporting_period__start_date__gte=recent_rps[3])
            staffer.fytd = calculate_utilization(tos_fytd)

        return billable_staff



            


    def get_context_data(self, **kwargs):
        context = super(GroupUtilizationView, self).get_context_data(**kwargs)
        context.update(
            {
                'unit_choices': UserData.UNIT_CHOICES,
            }
        )
        return context

    """
    Taken from Patrick's view--his template is expecting the following.
        context.update(
            {
                'unit_choices': UserData.objects.first().UNIT_CHOICES,
                'through_date': self.last_four_rp[0].end_date,
                'last_four_start_date': self.last_four_rp[len(self.last_four_rp)-1].start_date,
            }
        )
        
    """