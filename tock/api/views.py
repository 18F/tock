import collections
import datetime

from django.http import HttpResponse
from django.db import connection
from django.db.models import Sum

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from projects.models import Project
from hours.models import TimecardObject, Timecard, ReportingPeriod
from employees.models import UserData

from rest_framework import serializers, generics

import csv
from .renderers import stream_csv

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
        )
    billable = serializers.BooleanField(source='accounting_code.billable')
    profit_loss_account = serializers.CharField(source='profit_loss_account.name')
    client = serializers.StringRelatedField(source='accounting_code')

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
    is_billable = serializers.BooleanField()
    unit = serializers.SerializerMethodField()

    def get_unit(self,obj):
        return obj.get_unit_display()

class ReportingPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportingPeriod
        fields = (
            'start_date',
            'end_date',
        )

class TimecardSerializer(serializers.Serializer):
    user = serializers.StringRelatedField(source='timecard.user')
    project_id = serializers.CharField(source='project.id')
    project_name = serializers.CharField(source='project.name')
    profit_loss_account = serializers.CharField(source='project.profit_loss_account.name')
    hours_spent = serializers.DecimalField(max_digits=5, decimal_places=2)
    start_date = serializers.DateField(source='timecard.reporting_period.start_date')
    end_date = serializers.DateField(source='timecard.reporting_period.end_date')
    billable = serializers.BooleanField(source='project.accounting_code.billable')
    agency = serializers.CharField(source='project.accounting_code.agency.name')
    flat_rate = serializers.BooleanField(source='project.accounting_code.flat_rate')
    notes = serializers.CharField()
    revenue_profit_loss_account = serializers.CharField(
        source='revenue_profit_loss_account.accounting_string'
    )
    revenue_profit_loss_account_name = serializers.CharField(
        source='revenue_profit_loss_account.name'
    )
    expense_profit_loss_account = serializers.CharField(
        source='expense_profit_loss_account.accounting_string'
    )
    expense_profit_loss_account_name = serializers.CharField(
        source='expense_profit_loss_account.name'
    )

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
    """ This endpoint retrieves a list of users who have not filled out
    their time cards for a given time period """

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

class TimecardList(generics.ListAPIView):
    """ Endpoint for timecard data in csv or json """

    # Eagerly load related rows to avoid n+1 selects
    queryset = TimecardObject.objects.select_related(
        'timecard__user',
        'project__accounting_code__agency',
        'timecard__reporting_period',
    ).order_by(
        'timecard__reporting_period__start_date'
    )

    serializer_class = TimecardSerializer

    def get_queryset(self):
        return get_timecards(self.queryset, self.request.query_params)

def get_timecards(queryset, params=None):
    """
    Filter a TimecardObject queryset according to the provided GET
    query string parameters:

    * if `date` (in YYYY-MM-DD format) is provided, get rows for
      which the date falls within their reporting date range.

    * if `user` (in either `first.last` or numeric id) is provided,
      get rows for that user.

    * if `project` is provided as a numeric id or name, get rows for
      that project.
    """

    # include only submitted timecards unless submitted=no in params
    submitted = True
    if params and 'submitted' in params:
        submitted = params['submitted'] != 'no'
    queryset = queryset.filter(timecard__submitted=submitted)

    if not params:
        return queryset

    if 'date' in params:
        reporting_date = params.get('date')
        # TODO: validate YYYY-MM-DD format
        queryset = queryset.filter(
            timecard__reporting_period__start_date__lte=reporting_date,
            timecard__reporting_period__end_date__gte=reporting_date
        )

    if 'user' in params:
        # allow either user name or ID
        user = params.get('user')
        if user.isnumeric():
            queryset = queryset.filter(timecard__user__id=user)
        else:
            queryset = queryset.filter(timecard__user__username=user)

    if 'project' in params:
        # allow either project name or ID
        project = params.get('project')
        if project.isnumeric():
            queryset = queryset.filter(project__id=project)
        else:
            queryset = queryset.filter(project__name=project)

    if 'after' in params:
        # get everything after a specified date
        after_date = params.get('after')
        queryset = queryset.filter(
            timecard__reporting_period__end_date__gte=after_date
        )

    if 'billable' in params:
        # only pull records for billable projects
        billable = params.get('billable')
        queryset = queryset.filter(
            project__accounting_code__billable=billable
        )

    return queryset


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
