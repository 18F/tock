import os
import shutil
from unittest.mock import Mock, patch
import datetime

from django.core.exceptions import ValidationError
from django.conf import settings
from django.test import TestCase
from django.contrib.auth import get_user_model

import hours.models
import projects.models


class ReportingPeriodTests(TestCase):

  def setUp(self):
    self.reporting_period = hours.models.ReportingPeriod(
        start_date=datetime.date(2015, 1, 1),
        end_date=datetime.date(2015, 1, 7),
        working_hours=32)

  def tearDown(self):
    hours.models.ReportingPeriod.objects.all().delete()

  def test_reporting_period_save(self):
    self.assertEqual('2015-01-01', str(self.reporting_period))
    self.assertEqual(32, self.reporting_period.working_hours)

  def test_max_reporting_period_length(self):
    """Check to ensure a reporting period cannot be longer than 40 hours"""
    with self.assertRaises(ValidationError):
      hours.models.ReportingPeriod(start_date=datetime.date(2015, 1, 1),
                                   end_date=datetime.date(2015, 1, 7),
                                   working_hours=45).save()

  def test_get_fiscal_year(self):
    """Check to ensure the proper fiscal year is returned"""
    self.assertEqual(2015, self.reporting_period.get_fiscal_year())
    reporting_period_2 = hours.models.ReportingPeriod(
        start_date=datetime.date(2015, 10, 31),
        end_date=datetime.date(2015, 11, 7),
        working_hours=32)
    self.assertEqual(2016, reporting_period_2.get_fiscal_year())


class TimecardTests(TestCase):
  fixtures = ['projects/fixtures/projects.json', 'tock/fixtures/dev_user.json']

  def setUp(self):
    self.reporting_period = hours.models.ReportingPeriod.objects.create(
        start_date=datetime.date(2015, 1, 1),
        end_date=datetime.date(2015, 1, 7),
        working_hours=40)
    self.user = get_user_model().objects.get(id=1)
    self.timecard = hours.models.Timecard.objects.create(
        user=self.user,
        reporting_period=self.reporting_period)
    self.project_1 = projects.models.Project.objects.get(name="openFEC")
    self.project_2 = projects.models.Project.objects.get(name="Peace Corps")
    self.timecard_object_1 = hours.models.TimecardObject.objects.create(
        timecard=self.timecard,
        project=self.project_1,
        hours_spent=12)
    self.timecard_object_2 = hours.models.TimecardObject.objects.create(
        timecard=self.timecard,
        project=self.project_2,
        hours_spent=28)

  def tearDown(self):
    hours.models.ReportingPeriod.objects.all().delete()
    hours.models.Timecard.objects.all().delete()
    projects.models.Project.objects.all().delete()
    hours.models.TimecardObject.objects.all().delete()

  def test_timecard_string_return(self):
    """Ensure the returned string for the timecard is as expected"""
    self.assertEqual('test.user - 2015-01-01', str(self.timecard))
