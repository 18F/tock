# -*- coding: utf-8 -*-

import datetime

import factory
from factory.django import DjangoModelFactory

from django.contrib.auth.models import User

from hours import models
from projects.factories import ProjectFactory


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User


base_date = datetime.datetime(2015, 7, 4)
class ReportingPeriodFactory(DjangoModelFactory):
    class Meta:
        model = models.ReportingPeriod
    start_date = factory.Sequence(lambda n: base_date + datetime.timedelta(n))
    end_date = factory.Sequence(lambda n: base_date + datetime.timedelta(n + 6))


class TimecardFactory(DjangoModelFactory):
    class Meta:
        model = models.Timecard
    user = factory.SubFactory(UserFactory)
    reporting_period = factory.SubFactory(ReportingPeriodFactory)
    submitted = True


class TimecardObjectFactory(DjangoModelFactory):
    class Meta:
        model = models.TimecardObject
    timecard = factory.SubFactory(TimecardFactory)
    project = factory.SubFactory(ProjectFactory)
    hours_spent = 10
