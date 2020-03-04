from django.conf import settings
from django.contrib.auth import get_user_model

from .utils import (_build_utilization_context, calculate_utilization,
                    utilization_report)

User = get_user_model()

# Building context for display of employee level utilization data
def user_billing_context(user):
    """Build context dict for overall 18F utilization"""
    last_week = _get_employee_billing_data(user)
    last_month = _get_employee_billing_data(user, recent_periods=settings.RECENT_TIMECARDS_FOR_BILLABILITY)
    this_fy = _get_employee_billing_data(user, fiscal_year=True)

    return _build_utilization_context(last_week, last_month, this_fy)

def _get_employee_billing_data(user, recent_periods=None, fiscal_year=False):
    """
    Calculate 18f wide totals for a given time period
    """
    user_qs = User.objects.filter(id=user.id)

    if fiscal_year:
        start, end, utilization = utilization_report(user_qs, fiscal_year=fiscal_year)
    elif recent_periods:
        start, end, utilization = utilization_report(user_qs, recent_periods=recent_periods)
    else:
        start, end, utilization = utilization_report(user_qs)

    data = utilization.values('username', 'billable', 'total')[0]

    totals = {
        'billable': data['billable'],
        'total': data['total'],
        'utilization': calculate_utilization(data['billable'], data['total'])
    }
    return {'start_date': start, 'end_date': end, 'totals': totals}
