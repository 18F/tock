import datetime

from django.db.models import Sum

from hours.models import TimecardObject, ReportingPeriod

def get_timecardobjects(user):
    queryset = TimecardObject.objects.filter(
        user=user,
        timecard__submitted=True
    )
    queryset = queryset.exclude(
        project__name='Out of Office'
    )
    return queryset

def utilization_by_rp(queryset, date):
    """Limits TimecardObject queryset to objects that fall within a single
    ReportingPeriod."""
    queryset = queryset.filter(
        timecard__reporting_period__start_date__lte=date,
        timecard__reporting_period__end_date__gte=date
    )
    return queryset

def utilization_by_range(queryset, start_date, end_date):
    """Limits TimecardObject queryset to objectst that fall within a range of
    ReportingPeriod objects."""
    queryset = queryset.filter(
        timecard__reporting_period__start_date__gte=start_date,
        timecard__reporting_period__end_date__lte=end_date
    )
    return queryset

def calculate_utilization(queryset):
    """Calculates utilization, given a TimecardObject queryset."""
    all_hours = queryset.all().aggregate(
        Sum('hours_spent'))['hours_spent__sum']
    if all_hours:
        billable_hours = queryset.all().filter(
            project__accounting_code__billable=True).all().aggregate(
            Sum('hours_spent'))['hours_spent__sum']
        if billable_hours is None:
            billable_hours = 0
        utilization = '{:.3}%'.format((billable_hours / all_hours)*100)
        return utilization
    else:
        return 'No hours recorded.'

def get_fy_first_day(date):
    if date.month <= 9:
        year = date.year - datetime.datetimedelta(weeks=52)
    else:
        year = date.year
    target = datetime.date(year, 10, 1)

    return target

def get_rps_in_fy(target):
    n = len(ReportingPeriod.objects.filter(start_date__gt=target))
    return n

def get_last_n_rp(n, date):
    rp_queryset = ReportingPeriod.objects.filter(
        end_date__lte=date).order_by('-start_date')
    return rp_queryset[:n]
