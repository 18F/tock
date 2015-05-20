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

class ProjectList(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
