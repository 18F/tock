from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Sum, Q
from .utils import (_build_utilization_context, calculate_utilization,
                    utilization_report, limit_to_fy)

User = get_user_model()

# Building context for display of business unit level utilization data
def unit_billing_context(unit):
    """Build context dict for utilization by unit"""

    # all users who have created a timecard for this unit this FY
    users = User.objects.filter(Q(timecards__unit=unit), limit_to_fy()).distinct()

    last_week = _get_unit_billing_data(users, unit)
    last_month = _get_unit_billing_data(users, unit, recent_periods=settings.RECENT_TIMECARDS_FOR_BILLABILITY)
    this_fy = _get_unit_billing_data(users, unit, fiscal_year=True)

    context = _build_utilization_context(last_week, last_month, this_fy)

    # Add individual staff data to context
    staff_data = {
            'last_week_data': last_week['data'],
            'last_month_data': last_month['data'],
            'this_fy_data': this_fy['data']
    }
    context.update(staff_data)

    return context

def _get_unit_billing_data(users, unit, recent_periods=None, fiscal_year=False):
    """
    Calculate unit specific totals for a given time period
    and each employee therein
    """
    output_data = []
    totals = {
        'billable': 0,
        'denominator': 0,
        'utilization': calculate_utilization(0, 0)
    }

    if fiscal_year:
        start, end, utilization = utilization_report(users, fiscal_year=fiscal_year, unit=unit)
    elif recent_periods:
        start, end, utilization = utilization_report(users, recent_periods=recent_periods, unit=unit)
    else:
        start, end, utilization = utilization_report(users, unit=unit)

    if utilization:
        data = utilization.values('username', 'first_name', 'last_name', 'billable', 'target')
        # Build context for each employee
        output_data = [{
                'full_name': f"{employee['first_name']} {employee['last_name']}",
                'username': employee['username'],
                'denominator': employee['target'],
                'billable': employee['billable'],
                'utilization': calculate_utilization(employee['billable'], employee['target'])
                } for employee in data]

        # Get totals for unit
        unit_totals = data.aggregate(Sum('billable'), Sum('target'))

        totals = {'billable': unit_totals['billable__sum'],
        'denominator': unit_totals['target__sum'],
        'utilization': calculate_utilization(unit_totals['billable__sum'],unit_totals['target__sum'])
        }

    return {'start_date': start, 'end_date': end, 'data': output_data, 'totals': totals}
