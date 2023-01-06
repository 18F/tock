import collections
import datetime

from django.contrib.auth import get_user_model
from django.db import connection
from django.db.models import Count, F

from rest_framework import serializers, generics
from rest_framework.exceptions import ParseError

from hours.models import TimecardObject, Timecard, ReportingPeriod
from projects.models import Project
from employees.models import UserData

User = get_user_model()

# Serializers for different models

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            'id',
            'client',
            'name',
            'description',
            'billable',
            'start_date',
            'end_date',
            'active',
            'profit_loss_account',
            'organization',
        )
    billable = serializers.BooleanField(source='accounting_code.billable')
    profit_loss_account = serializers.CharField(source='profit_loss_account.name', allow_null=True)
    client = serializers.StringRelatedField(source='accounting_code')
    organization = serializers.StringRelatedField()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email'
        )

class UserDataSerializer(serializers.Serializer):
    user = serializers.StringRelatedField()
    current_employee = serializers.BooleanField()
    is_18f_employee = serializers.BooleanField()
    is_active = serializers.BooleanField()
    is_billable = serializers.BooleanField()
    unit = serializers.StringRelatedField()
    organization = serializers.StringRelatedField()

    def get_unit(self,obj):
        return obj.unit

class ReportingPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportingPeriod
        fields = (
            'start_date',
            'end_date',
            'exact_working_hours',
            'min_working_hours',
            'max_working_hours',
        )

class SubmissionSerializer(serializers.Serializer):
    user = serializers.CharField(source='id')
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.CharField()
    on_time_submissions = serializers.CharField(source='tcount')

class TimecardSerializer(serializers.Serializer):
    user = serializers.StringRelatedField(source='timecard.user')
    project_id = serializers.CharField(source='project.id')
    project_name = serializers.CharField(source='project.name')
    profit_loss_account = serializers.CharField(
        source='project.profit_loss_account.name',
        allow_null=True
    )
    hours_spent = serializers.DecimalField(max_digits=5, decimal_places=2)
    project_allocation = serializers.DecimalField(max_digits=6, decimal_places=3)
    start_date = serializers.DateField(
        source='timecard.reporting_period.start_date'
    )
    end_date = serializers.DateField(
        source='timecard.reporting_period.end_date'
    )
    billable = serializers.BooleanField(
        source='project.accounting_code.billable'
    )
    agency = serializers.CharField(
        source='project.accounting_code.agency.name'
    )
    flat_rate = serializers.BooleanField(
        source='project.accounting_code.flat_rate'
    )
    notes = serializers.CharField()
    billable_expectation = serializers.CharField(
        source='timecard.billable_expectation'
    )
    employee_organization = serializers.CharField(
        source='timecard.user.user_data.organization_name'
    )
    project_organization = serializers.CharField(
        source='project.organization_name'
    )
    grade = serializers.IntegerField(
        source='grade.grade',
        allow_null=True
    )

class FullTimecardSerializer(serializers.ModelSerializer):
    # Fields that require accessing other models
    user_name = serializers.CharField(source='user.username')
    reporting_period_start_date = serializers.DateField(source='reporting_period.start_date')
    reporting_period_end_date = serializers.DateField(source='reporting_period.end_date')

    class Meta:
        model = Timecard
        fields = [
            # straight pass-through fields
            'id',
            'submitted',
            'submitted_date',
            'billable_expectation',
            'target_hours',
            'billable_hours',
            'non_billable_hours',
            'excluded_hours',
            'utilization',
            # fields from other models
            'user_name',
            'reporting_period_start_date',
            'reporting_period_end_date',
        ]

# API Views

class UserDataView(generics.ListAPIView):
    queryset = UserData.objects.all()
    serializer_class = UserDataSerializer

class ProjectList(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class ProjectInstanceView(generics.RetrieveAPIView):
    """ Return the details of a specific project """
    queryset =  Project.objects.all()
    model = Project
    serializer_class = ProjectSerializer

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ReportingPeriodList(generics.ListAPIView):
    queryset = ReportingPeriod.objects.all()
    serializer_class = ReportingPeriodSerializer

class ReportingPeriodAudit(generics.ListAPIView):
    """
    Retrieves a list of users who have not filled out
    their time cards for a given time period
    """

    queryset = ReportingPeriod.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'start_date'

    def get_queryset(self):
        reporting_period = self.queryset.get(
            start_date=datetime.datetime.strptime(
                self.kwargs['reporting_period_start_date'], "%Y-%m-%d"
            ).date()
        )
        filed_users = list(
            Timecard.objects.filter(
                reporting_period=reporting_period,
                submitted=True
            ).distinct().all().values_list('user__id', flat=True))
        return get_user_model().objects \
            .exclude(user_data__start_date__gte=reporting_period.end_date) \
            .exclude(id__in=filed_users) \
            .filter(user_data__current_employee=True) \
            .order_by('last_name', 'first_name')

class Submissions(generics.ListAPIView):
    """
    Returns a list of users and the number of timecards they have
    submitted on time since the requested reporting period
    """

    serializer_class = SubmissionSerializer

    def get_queryset(self):
        rp_num = self.kwargs['num_past_reporting_periods']

        reporting_period = list(ReportingPeriod.get_most_recent_periods(
            number_of_periods=rp_num
        ))[-1]

        # filter to punctually submitted timecards
        # between the requested period and today
        today = datetime.date.today()
        timecards = Timecard.objects.filter(
            reporting_period__end_date__lt=today,
            reporting_period__end_date__gte=reporting_period.end_date,
            submitted_date__lte=F('reporting_period__end_date')
        )

        return get_user_timecard_count(timecards)

class FullTimecardList(generics.ListAPIView):
    serializer_class = FullTimecardSerializer

    def get_queryset(self):
        # Lookup the associated user and reporting_period in the original
        # query since we'll be accessing them later. See https://docs.djangoproject.com/en/3.2/ref/models/querysets/#django.db.models.query.QuerySet.select_related
        queryset = Timecard.objects.select_related(
            'user',
            'reporting_period',
        )
        return filter_timecards(queryset, self.request.query_params)

class TimecardList(generics.ListAPIView):
    """ Endpoint for timecard data in csv or json """

    # Eagerly load related rows to avoid n+1 selects
    queryset = TimecardObject.objects.select_related(
        'timecard__user',
        'project__accounting_code__agency',
        'timecard__reporting_period',
        'grade',
    ).order_by(
        'timecard__reporting_period__start_date'
    )

    serializer_class = TimecardSerializer

    def get_queryset(self):
        return get_timecardobjects(self.queryset, self.request.query_params)


def date_from_iso_format(date_str):
    try:
        return datetime.date.fromisoformat(date_str)
    except ValueError:
        raise ParseError(
            detail='Invalid date format. Got {}, expected ISO format (YYYY-MM-DD)'.format(
                date_str
            )
        )

def filter_timecards(queryset, params={}):
    """
    Filter a queryset of timecards according to the provided query
    string parameters.

    * `date`: filter for reporting periods that contain this date
    * `user`: either username or numeric id for a user
    * `after`: the reporting period ends after the given date
    * `before`: the reporting period starts before the given date
    """
    submitted_param = params.get("submitted", "yes")  # default to only submitted cards
    submitted = (submitted_param != "no")
    queryset = queryset.filter(submitted=submitted)

    if not params:
        return queryset

    if 'date' in params:
        reporting_date = date_from_iso_format(params.get('date'))
        queryset = queryset.filter(
            reporting_period__start_date__lte=reporting_date,
            reporting_period__end_date__gte=reporting_date
        )

    if 'user' in params:
        # allow either user name or ID
        user = params.get('user')
        if user.isnumeric():
            queryset = queryset.filter(user__id=user)
        else:
            queryset = queryset.filter(user__username=user)

    if 'after' in params:
        # get everything after a specified date
        after_date = date_from_iso_format(params.get('after'))
        queryset = queryset.filter(
            reporting_period__end_date__gte=after_date
        )

    if 'before' in params:
        # get everything before a specified date
        before_date = date_from_iso_format(params.get('before'))
        queryset = queryset.filter(
            reporting_period__start_date__lte=before_date
        )

    if 'org' in params:
        # filter on organization, "0" to include all orgs, "None" for
        # "organization IS NULL"
        org_id = params.get('org')
        if org_id.isnumeric() and org_id != "0": # 0 indicates all organizations, no filtering then
            queryset = queryset.filter(user__user_data__organization__id=org_id)
        elif org_id.lower() == "none":  # the only allowable value that isn't numeric is None
            queryset = queryset.filter(user__user_data__organization__isnull=True)

    return queryset



def get_timecardobjects(queryset, params={}):
    """
    Filter a TimecardObject queryset according to the provided GET
    query string parameters:

    * `project`: numeric id or name of a project
    * `billable`: `True` or `False` to filter for projects that are or aren't billable
    """

    # queryset as passed is a queryset of TimecardObjects. Get a queryset of
    # the matching Timecards that we can filter...
    timecard_queryset = Timecard.objects.filter(timecardobjects__in=queryset)
    timecard_queryset = filter_timecards(timecard_queryset, params)
    # and now sub-select the matching timecardobjects from our original
    # queryset
    queryset = queryset.filter(timecard__in=timecard_queryset)

    if 'project' in params:
        # allow either project name or ID
        project = params.get('project')
        if project.isnumeric():
            queryset = queryset.filter(project__id=project)
        else:
            queryset = queryset.filter(project__name=project)

    if 'billable' in params:
        # only pull records for billable projects
        billable = params.get('billable')
        queryset = queryset.filter(
            project__accounting_code__billable=billable
        )

    return queryset

def get_user_timecard_count(queryset):
    """
    Get a list of users and the number of the timecards
    from a queryset of timecards passed in
    """
    timecard_ids = queryset.values_list('id', flat=True)
    user_timecard_counts = User.objects.filter(
        timecards__id__in=timecard_ids
    ).annotate(
        tcount=Count('timecards')
    )
    return user_timecard_counts


from rest_framework.response import Response
from rest_framework.decorators import api_view

hours_by_quarter_query = '''
with agg as (
    select
        extract(year from rp.start_date) +
            (extract(month from rp.start_date) / 10) as year,
        (extract(month from rp.start_date) + 3 - 1)::int % 12 / 3 + 1 as quarter,
        billable,
        sum(hours_spent) as hours
    from hours_timecardobject tco
    join hours_timecard tc on tco.timecard_id = tc.id
    join hours_reportingperiod rp on tc.reporting_period_id = rp.id
    join projects_project pr on tco.project_id = pr.id
    join projects_accountingcode ac on pr.accounting_code_id = ac.id
    where tc.submitted = True
    group by
        year,
        quarter,
        billable
)
select
    year,
    quarter,
    coalesce(max(case when billable then hours else null end), 0) as billable,
    coalesce(max(case when not billable then hours else null end), 0) as nonbillable,
    sum(hours) as total
from agg
group by
    year,
    quarter
'''

HoursByQuarter = collections.namedtuple(
    'HoursByQuarter',
    ['year', 'quarter', 'billable', 'nonbillable', 'total'],
)

class HoursByQuarterSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    quarter = serializers.IntegerField()
    billable = serializers.FloatField()
    nonbillable = serializers.FloatField()
    total = serializers.FloatField()

@api_view()
def hours_by_quarter(request, *args, **kwargs):
    cursor = connection.cursor()
    cursor.execute(hours_by_quarter_query)
    rows = cursor.fetchall()
    return Response([
        HoursByQuarterSerializer(HoursByQuarter(*each)).data
        for each in rows
    ])

hours_by_quarter_by_user_query = '''
with agg as (
    select
        extract(year from rp.start_date) +
            (extract(month from rp.start_date) / 10) as year,
        (extract(month from rp.start_date) + 3 - 1)::int % 12 / 3 + 1 as quarter,
        username,
        billable,
        sum(hours_spent) as hours
    from hours_timecardobject tco
    join hours_timecard tc on tco.timecard_id = tc.id
    join hours_reportingperiod rp on tc.reporting_period_id = rp.id
    join auth_user usr on tc.user_id = usr.id
    join projects_project pr on tco.project_id = pr.id
    join projects_accountingcode ac on pr.accounting_code_id = ac.id
    where tc.submitted = True
    group by
        year,
        quarter,
        username,
        billable
)
select
    year,
    quarter,
    username,
    coalesce(max(case when billable then hours else null end), 0) as billable,
    coalesce(max(case when not billable then hours else null end), 0) as nonbillable,
    sum(hours) as total
from agg
group by
    year,
    quarter,
    username
'''

HoursByQuarterByUser = collections.namedtuple(
    'HoursByQuarter',
    ['year', 'quarter', 'username', 'billable', 'nonbillable', 'total'],
)

class HoursByQuarterByUserSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    quarter = serializers.IntegerField()
    username = serializers.CharField()
    billable = serializers.FloatField()
    nonbillable = serializers.FloatField()
    total = serializers.FloatField()

@api_view()
def hours_by_quarter_by_user(request, *args, **kwargs):
    cursor = connection.cursor()
    cursor.execute(hours_by_quarter_by_user_query)
    rows = cursor.fetchall()
    return Response([
        HoursByQuarterByUserSerializer(HoursByQuarterByUser(*each)).data
        for each in rows
    ])
