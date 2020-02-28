import datetime

from hours.models import ReportingPeriod
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.contrib.auth import get_user_model

User = get_user_model()

def calculate_utilization(billable_hours, all_hours):
    """Calculates utilization as hours billed divided by hours worked."""
    if not all_hours:
        return 'No hours submitted.'
    if not billable_hours:
        return '0.00%'
    return '{:.3}%'.format((billable_hours / all_hours * 100))

def _build_utilization_query(users=None,recent_periods=None, fiscal_year=False):
    """
    Construct queryset to filter and aggregate timecards for utilization reportings

    Traversing Models from User to individual Timecards and project lines.

    Excluding project lines where:
        exclude_from_billability == False

    Parameters:
        users - A Queryset of User for which we'll calculate utilization
        recent_periods - ReportingPeriods we'll aggregate to calculate utilization
        fiscal_year - If True, aggregate utilization from the beginning of the current fiscal year
    """

    billable_base_filter = Q(timecards__timecardobjects__project__accounting_code__billable=True)
    non_billable_base_filter = Q(timecards__timecardobjects__project__accounting_code__billable=False,
                          timecards__timecardobjects__project__exclude_from_billability=False)

    if not fiscal_year:
        billable_filter = billable_base_filter & _limit_to_recent_periods(recent_periods)
        non_billable_filter = non_billable_base_filter & _limit_to_recent_periods(recent_periods)
    else:
        billable_filter = billable_base_filter & _limit_to_fy()
        non_billable_filter = non_billable_base_filter & _limit_to_fy()

    # Using Coalesce to set a default value of 0 if no data is available
    billable = Coalesce(Sum('timecards__timecardobjects__hours_spent', filter=billable_filter), 0)
    non_billable = Coalesce(Sum('timecards__timecardobjects__hours_spent', filter=non_billable_filter), 0)
    if users:
        return users.annotate(billable=billable).annotate(non_billable=non_billable).annotate(total=billable + non_billable)
    raise NotImplementedError

def utilization_report(user_qs=None,recent_periods=1, fiscal_year=False):
    """
    Return start/end dates from which we aggregated timecard instances over which we'll aggregate
    AND the resulting data of that aggregation

    Parameters:
    users - A Queryset of User for which we'll calculate utilization
    recent_periods - Number of previous reporting periods, from now, we'll include
    fiscal_year - If True, aggregate data from the beginning of the current fiscal year
    """
    users = utilization_users_queryset(user_qs).order_by('username')
    start_date, end_date, recent_periods = _get_reporting_periods(recent_periods)
    utilization_data = _build_utilization_query(users=users, recent_periods=recent_periods, fiscal_year=fiscal_year)
    return (start_date, end_date, utilization_data)

def users_to_include_for_utilization():
    """
    Limit to users which should be included in utilization reports
    """
    return Q(user_data__is_billable=True,
             is_active=True,
             user_data__current_employee=True)

def utilization_users_queryset(qs):
    """
    Build initial User QuerySet for utilization reporting
    """
    if qs:
        return qs.filter(users_to_include_for_utilization())
    return User.objects.none()

def _limit_to_recent_periods(reporting_periods):
    """
    Filter component to restrict timecards to those associated with
    the provided reporting_periods
    """
    return Q(timecards__reporting_period__in=reporting_periods)

def _limit_to_fy():
    """
    Filter component to Limit timecard aggregation to the current fiscal year
    """
    current_fy = ReportingPeriod().get_fiscal_year_from_date(datetime.date.today())
    fy_start_date = ReportingPeriod().get_fiscal_year_start_date(current_fy)
    return Q(timecards__reporting_period__start_date__gte=fy_start_date)

def _get_reporting_periods(count):
    """
    Return
    """
    rps = ReportingPeriod.get_most_recent_periods(number_of_periods=count)
    start_date = rps[count - 1].start_date
    end_date = rps[0].end_date
    return start_date, end_date, rps

def _build_utilization_context(last_week, last_month, this_fy):
    """Build shared context components of utilization reports"""

    return {
            'last_week_start_date': last_week['start_date'],
            'last_week_end_date': last_week['end_date'],
            'last_week_totals': last_week['totals'],
            'last_month_start_date': last_month['start_date'],
            'last_month_end_date': last_month['end_date'],
            'last_month_totals': last_month['totals'],
            'this_fy_end_date': this_fy['end_date'],
            'this_fy_totals': this_fy['totals'],
    }
