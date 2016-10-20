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
        all_hours = 0
        for i in timecardobjects:
            all_hours += i.hours_spent
        if all_hours is (False or 0):
            return 'No hours submitted.'
        else:
            billable_hours = 0
            for i in timecardobjects:
                if i.project.accounting_code.billable:
                    billable_hours += i.hours_spent
                else:
                    pass
            if billable_hours is (None or 0):
                return '0.00%'
            else:
                return '{:.3}%'.format((billable_hours / all_hours * 100))

    def get_queryset(self):
        """Gets submitted timecards limited to the reporting periods in
        question."""
        tos_fytd = TimecardObject.objects.filter(
            submitted=True,
            timecard__reporting_period__start_date__gte=recent_rps[4],
            timecard__user__user_data__is_billable=True,
            timecard__user__user_data__current_employee=True
        ).prefetch_related(
            'timecard__user'
        ).prefetch_related(
            'timecard__reporting_period'
        ).prefetch_related(
            'project__accounting_code'
        )

        print(tos_fytd[0].__dict__)

        tos_recent = tos_fytd.filter(
            timecard__reporting_period__start_date__gte=recent_rps[1])

        tos_last = tos_recent.filter(
            timecard__reporting_period__start_date__gte=recent_rps[0][0].start_date)

        billable_staff_set = User.objects.filter(
            user_data__is_billable=True
        ).select_related('user_data')

        for staffer in billable_staff_set:

            """Calculate utilization for fiscal year to lastest reporting
            period."""
            tos_fytd_staffer = list()
            for i in tos_fytd:
                if i.timecard.user == staffer:
                    tos_fytd_staffer.append(i)
                else:
                    pass
            staffer.fytd = self.calculate_utilization(tos_fytd_staffer)

            """Calc for recent rps."""
            tos_recent_staffer = list()
            for i in tos_recent:
                if i.timecard.user == staffer:
                    tos_recent_staffer.append(i)
                else:
                    pass
            staffer.recent = self.calculate_utilization(tos_recent_staffer)

            """Calc for last rps."""
            tos_last_staffer = list()
            for i in tos_last:
                if i.timecard.user == staffer:
                    tos_last_staffer.append(i)
                else:
                    pass
            staffer.last = self.calculate_utilization(tos_last_staffer)
        return billable_staff_set

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
