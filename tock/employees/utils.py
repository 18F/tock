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
        billable_hours = tos.all().filter(
            project__accounting_code__billable=True).all().aggregate(
            Sum('hours_spent'))['hours_spent__sum']
        utilization = '{:.3}%'.format((billable_hours / all_hours)*100)
        return utilization
    else:
        return 'No hours recorded.'
