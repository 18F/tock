from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.conf import settings
from django.db.models import Count, Sum
from decimal import Decimal

from django.contrib.auth.models import User, Group
from hours.models import ReportingPeriod, Timecard, TimecardObject
from projects.models import Project, Agency, AccountingCode

from rest_framework import serializers
from rest_framework import generics

class ProjectSerializer(serializers.ModelSerializer):
    billable = serializers.BooleanField(source='accounting_code.billable')
    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'billable',)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name',)

class TimecardSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(source='timecard.user')
    project = serializers.CharField(source='project.name')
    start_date = serializers.DateField(source='timecard.reporting_period.start_date')
    end_date = serializers.DateField(source='timecard.reporting_period.end_date')
    billable = serializers.BooleanField(source='project.accounting_code.billable')
    class Meta:
        model = TimecardObject
        fields = ('user', 'project', 'start_date', 'end_date', 'hours_spent', 'billable',)

class ProjectList(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class TimecardList(generics.ListAPIView):
    serializer_class = TimecardSerializer

    def get_queryset(self):
        params = self.request.QUERY_PARAMS
        queryset = TimecardObject.objects.all()

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
