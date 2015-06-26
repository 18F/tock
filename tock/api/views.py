from django.http import HttpResponse
from django.db.models import Sum

from django.contrib.auth.models import User
from projects.models import Project
from hours.models import TimecardObject

from rest_framework import serializers, generics, pagination

import csv
from .renderers import stream_csv

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

class TimecardSerializer(serializers.Serializer):
    user = serializers.StringRelatedField(source='timecard.user')
    project_id = serializers.CharField(source='project.id')
    project_name = serializers.CharField(source='project.name')
    hours_spent = serializers.DecimalField(max_digits=5, decimal_places=2)
    start_date = serializers.DateField(source='timecard.reporting_period.start_date')
    end_date = serializers.DateField(source='timecard.reporting_period.end_date')
    billable = serializers.BooleanField(source='project.accounting_code.billable')

class BulkTimecardSerializer(serializers.Serializer):
    project_name = serializers.CharField(source='project.name')
    project_id = serializers.CharField(source='project.id')
    employee = serializers.StringRelatedField(source='timecard.user')
    start_date = serializers.DateField(source='timecard.reporting_period.start_date')
    end_date = serializers.DateField(source='timecard.reporting_period.end_date')
    hours_spent = serializers.DecimalField(max_digits=5, decimal_places=2)
    billable = serializers.BooleanField(source='project.accounting_code.billable')
    modified_date = serializers.DateTimeField(source='modified', format='%Y-%m-%d %H:%M:%S')

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

def timeline_view(request, value_fields=(), **field_alias):
    queryset = get_timecards(TimecardList.queryset, request.GET)

    fields = list(value_fields) + [
        'timecard__reporting_period__start_date',
        'timecard__reporting_period__end_date',
        'project__accounting_code__billable'
    ]

    field_map = {
        'timecard__reporting_period__start_date': 'start_date',
        'timecard__reporting_period__end_date': 'end_date',
        'project__accounting_code__billable': 'billable',
    }
    field_map.update(field_alias)

    data = queryset.values(*fields).annotate(hours_spent=Sum('hours_spent'))

    fields.append('hours_spent')

    data = [
        {
            field_map.get(field, field): row.get(field)
            for field in fields
        }
        for row in data
    ]

    response = HttpResponse(content_type='text/csv')

    fieldnames = [field_map.get(field, field) for field in fields]
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    return response

def project_timeline_view(request):
    return timeline_view(
        request,
        value_fields=['project__id', 'project__name'],
        project__id='project_id',
        project__name='project_name',
    )

def user_timeline_view(request):
    return timeline_view(
        request,
        value_fields=['timecard__user__username'],
        timecard__user__username='user',
    )

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

    return queryset


def bulk_timecard_list(request):
    """
    Stream all the timecards as CSV.
    """
    queryset = get_timecards(TimecardList.queryset, request.GET)
    serializer = BulkTimecardSerializer()
    return stream_csv(queryset, serializer)
