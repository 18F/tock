from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Sum

from .utils import (_build_utilization_context, calculate_utilization,
                    utilization_report)

User = get_user_model()

def unit_billing_context(unit):
    """Build context dict for utilization by unit"""
    last_week = _get_unit_billing_data(unit)
    last_month = _get_unit_billing_data(unit, recent_periods=settings.RECENT_TIMECARDS_FOR_BILLABILITY)
    this_fy = _get_unit_billing_data(unit, fiscal_year=True)

    context = _build_utilization_context(last_week, last_month, this_fy)

    # Add individual staff data to context
    staff_data = {
            'last_week_data': last_week['data'],
            'last_month_data': last_month['data'],
            'this_fy_data': this_fy['data'],
    }
    context.update(staff_data)

    return context

def _get_unit_billing_data(unit, recent_periods=None, fiscal_year=False):
    """
    Calculate unit specific totals for a given time period
    and each employee therein
    """
    users = User.objects.filter(user_data__unit=unit)
    if fiscal_year:
        start, end, utilization = utilization_report(users, fiscal_year=fiscal_year)
    elif recent_periods:
        start, end, utilization = utilization_report(users, recent_periods=recent_periods)
    else:
        start, end, utilization = utilization_report(users)

    data = utilization.values('username', 'billable', 'total')

    # Build context for each employee
    output_data = [{
            'username': employee['username'],
            'total': employee['total'],
            'billable': employee['billable'],
            'utilization': calculate_utilization(employee['billable'], employee['total'])
            } for employee in data]

    # Get totals for unit
    unit_totals = data.aggregate(Sum('billable'), Sum('total'))

    totals = {'billable': unit_totals['billable__sum'],
    'total': unit_totals['total__sum'],
    'utilization': calculate_utilization(unit_totals['billable__sum'],unit_totals['total__sum'])
    }

    return {'start_date': start, 'end_date': end, 'data': output_data, 'totals': totals}
