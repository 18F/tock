import datetime

from hours.models import ReportingPeriod

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

    # Grab last n reporting periods with an end date that is less than today.
    reportingperiods = ReportingPeriod.objects.filter(
        end_date__lt=today).order_by('-start_date')[:periods]

    # Grab end date of last reporting period.
    reportingperiods_end_date = reportingperiods[0].end_date

    # Grab start date of first reporting period.
    reportingperiods_start_date = reportingperiods[periods - 1].start_date

    # Set the earliest date from which TimecardObjects need to be queried.
    if reportingperiods_start_date <= fy_first_day:
        earliest_date = reportingperiods_start_date
    else:
        earliest_date = fy_first_day

    latest_start_date = reportingperiods[0].start_date

    return reportingperiods_end_date, reportingperiods_start_date, \
        fy_first_day, earliest_date, latest_start_date

"""Calculates utilization as hours billed divided by hours worked."""
def calculate_utilization(billable_hours, all_hours):
    if all_hours is (None or 0):
        return 'No hours submitted.'
    else:
        if billable_hours is None:
            return '0.00%'
        else:
            return '{:.3}%'.format((billable_hours / all_hours * 100))
