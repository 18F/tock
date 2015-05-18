import os
import shutil
import datetime
from unittest.mock import Mock, patch

from django.conf import settings
from django.test import TestCase
from django.contrib.auth import get_user_model

import hours.models
import projects.models
from hours.templatetags.has_submitted_timesheet import has_submitted_timesheet


class TemplateTagTests(TestCase):
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
        project=self.project_1)
    self.timecard_object_2 = hours.models.TimecardObject.objects.create(
        timecard=self.timecard,
        project=self.project_2)

  def tearDown(self):
    hours.models.ReportingPeriod.objects.all().delete()
    hours.models.Timecard.objects.all().delete()
    projects.models.Project.objects.all().delete()
    hours.models.TimecardObject.objects.all().delete()

  def test_has_submitted_timesheet(self):
    self.assertTrue(has_submitted_timesheet(self.user, self.reporting_period))
    user2 = get_user_model().objects.create(id=2)
    self.assertFalse(has_submitted_timesheet(user2, self.reporting_period))
