from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Sum

from .utils import (_build_utilization_context, calculate_utilization,
                    utilization_report)

User = get_user_model()

# Building context for display of business unit level utilization data
def unit_billing_context(unit):
    """Build context dict for utilization by unit"""

    # all users that have ever created a timecard for this unit
    users = User.objects.filter(timecards__unit=unit).distinct()

    last_week = _get_unit_billing_data(users, unit)
    last_month = _get_unit_billing_data(users, unit, recent_periods=settings.RECENT_TIMECARDS_FOR_BILLABILITY)
    this_fy = _get_unit_billing_data(users, unit, fiscal_year=True)

    context = _build_utilization_context(last_week, last_month, this_fy)

    usernames_without_hours = [e.username for e in _employees_without_hours(users, last_week['data'] + last_month['data'] + this_fy['data'])]

    # Add individual staff data to context
    staff_data = {
            'last_week_data': [data for data in last_week['data'] if data['username'] not in usernames_without_hours],
            'last_month_data': [data for data in last_month['data'] if data['username'] not in usernames_without_hours],
            'this_fy_data': [data for data in this_fy['data'] if data['username'] not in usernames_without_hours],
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
        data = utilization.values('username', 'billable', 'target')

        # Build context for each employee
        output_data = [{
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

def _employee_has_no_hours(employee, billing_data):
    """
    The denominator field in the billing data represents the employee's target hours. If the target hours for an employee across all
    of the billing data sums to zero, then they have not logged any hours applicable to utilization.
    """
    return sum(filter(None, [employee_data['denominator'] for employee_data in billing_data if employee_data['username'] == employee.username])) == 0

def _employees_without_hours(employees, flattened_billing_data):
    """
    Return a list of all employees that have no logged hours for the provided billing data
    """
    return list(filter(lambda e: _employee_has_no_hours(e, flattened_billing_data), employees))
