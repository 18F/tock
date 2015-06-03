from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.conf import settings
from django.db.models import Count, Sum
from decimal import Decimal

from django.contrib.auth.models import User
from projects.models import Project
from hours.models import TimecardObject

from rest_framework import serializers, generics, pagination, renderers

import csv
from .renderers import PaginatedCSVRenderer, stream_csv

class StandardResultsSetPagination(pagination.PageNumberPagination):
    """
    This is a standard results set paginator for all API view classes
    that need pagination.
    """
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500


# Serializers for different models

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            'id',
            'name',
            'description',
            'billable',
        )
    billable = serializers.BooleanField(source='accounting_code.billable')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
        )

class TimecardSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimecardObject
        fields = (
            'user',
            'project_name',
            'project_id',
            'start_date',
            'end_date',
            'hours_spent',
            'billable',
        )
    user = serializers.StringRelatedField(source='timecard.user')
    project_id = serializers.CharField(source='project.id')
    project_name = serializers.CharField(source='project.name')
    start_date = serializers.DateField(source='timecard.reporting_period.start_date')
    end_date = serializers.DateField(source='timecard.reporting_period.end_date')
    billable = serializers.BooleanField(source='project.accounting_code.billable')

class BulkTimecardSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimecardObject
        fields = (
            'project_name',
            'project_id',
            'billable',
            'employee',
            'start_date',
            'end_date',
            'modified_date',
            'hours_spent',
        )
    project_name = serializers.CharField(source='project.name')
    project_id = serializers.CharField(source='project.id')
    billable = serializers.BooleanField(source='project.accounting_code.billable')
    employee = serializers.StringRelatedField(source='timecard.user')
    start_date = serializers.DateField(source='timecard.reporting_period.start_date')
    end_date = serializers.DateField(source='timecard.reporting_period.end_date')
    modified_date = serializers.DateTimeField(source='modified')

    def to_representation(self, obj, *args, **kwargs):
        data = super(BulkTimecardSerializer, self).to_representation(obj, *args, **kwargs)
        data['modified_date'] = obj.modified.strftime('%Y-%m-%d %H:%M:%S')
        return data

# API Views

class ProjectList(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    pagination_class = StandardResultsSetPagination

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination

class TimecardList(generics.ListAPIView):
    queryset = TimecardObject.objects.order_by('timecard__reporting_period__start_date')

    serializer_class = TimecardSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return get_timecards(self.queryset, self.request.QUERY_PARAMS)

def ProjectTimelineView(request):
    queryset = get_timecards(TimecardList.queryset, request.GET)

    data = queryset.values(
        'project__id',
        'project__name',
        # 'timecard__user__username',
        'timecard__reporting_period__start_date',
        # 'timecard__reporting_period__end_date',
        'project__accounting_code__billable'
    ).annotate(hours_spent=Sum('hours_spent'))

    fields = (
        ('project_id', 'project__id'),
        ('project_name', 'project__name'),
        ('start_date', 'timecard__reporting_period__start_date'),
        ('billable', 'project__accounting_code__billable'),
        ('hours_spent', 'hours_spent'),
    )

    def map_row(row):
        return dict(
            (dest, row.get(src)) for (dest, src) in fields
        )

    data = map(map_row, data)

    response = HttpResponse(content_type='text/csv')
    fieldnames = [f[0] for f in fields]
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    return response

def get_timecards(queryset, params={}):
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

    return queryset



def bulk_timecard_list(request):
    """
    Stream all the timecards as CSV.
    """
    queryset = get_timecards(TimecardList.queryset, request.GET)
    serializer = BulkTimecardSerializer()
    return stream_csv(queryset, serializer)
