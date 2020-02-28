from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Sum

from .utils import (_build_utilization_context, calculate_utilization,
                    utilization_report)

User = get_user_model()

def org_billing_context():
    """Build context dict for overall 18F utilization"""
    last_week = _get_18f_billing_data()
    last_month = _get_18f_billing_data(recent_periods=settings.RECENT_TIMECARDS_FOR_BILLABILITY)
    this_fy = _get_18f_billing_data(fiscal_year=True)

    return _build_utilization_context(last_week, last_month, this_fy)

def _get_18f_billing_data(recent_periods=None, fiscal_year=False):
    """
    Calculate 18f wide totals for a given time period
    """
    user_qs = User.objects.filter()

    if fiscal_year:
        start, end, utilization = utilization_report(user_qs, fiscal_year=fiscal_year)
    elif recent_periods:
        start, end, utilization = utilization_report(user_qs, recent_periods=recent_periods)
    else:
        start, end, utilization = utilization_report(user_qs)

    org_totals = utilization.values('billable', 'total').aggregate(Sum('billable'), Sum('total'))

    totals = {
        'billable': org_totals['billable__sum'],
        'total': org_totals['total__sum'],
        'utilization': calculate_utilization(org_totals['billable__sum'], org_totals['total__sum'])
    }
    return {'start_date': start, 'end_date': end, 'totals': totals}
