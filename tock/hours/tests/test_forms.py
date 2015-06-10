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

from hours.forms import TimecardForm, TimecardObjectForm, TimecardFormSet, TimecardInlineFormSet


class TimecardFormTests(TestCase):
  fixtures = ['projects/fixtures/projects.json', 'tock/fixtures/dev_user.json']

  def setUp(self):
    self.reporting_period = hours.models.ReportingPeriod.objects.create(
        start_date=datetime.date(2015, 1, 1),
        end_date=datetime.date(2015, 1, 7),
        working_hours=40)
    self.user = get_user_model().objects.get(id=1)
    self.project_1 = projects.models.Project.objects.get(name="openFEC")
    self.project_2 = projects.models.Project.objects.get(name="Peace Corps")

  def tearDown(self):
    hours.models.ReportingPeriod.objects.all().delete()
    hours.models.Timecard.objects.all().delete()
    projects.models.Project.objects.all().delete()
    hours.models.TimecardObject.objects.all().delete()

  def test_valid_form(self):
    form_data = {'user': self.user, 'reporting_period': self.reporting_period}
    form = TimecardForm(form_data)
    self.assertTrue(form.is_valid())


class TimecardObjectFormTests(TestCase):
  fixtures = ['projects/fixtures/projects.json', 'tock/fixtures/dev_user.json']

  def setUp(self):
    self.reporting_period = hours.models.ReportingPeriod.objects.create(
        start_date=datetime.date(2015, 1, 1),
        end_date=datetime.date(2015, 1, 7),
        working_hours=40)
    self.user = get_user_model().objects.get(id=1)
    self.project_1 = projects.models.Project.objects.get(name="openFEC")
    self.project_2 = projects.models.Project.objects.get(name="Peace Corps")

  def tearDown(self):
    hours.models.ReportingPeriod.objects.all().delete()
    hours.models.Timecard.objects.all().delete()
    projects.models.Project.objects.all().delete()
    hours.models.TimecardObject.objects.all().delete()

  def xtest_add_project(self):
    form_data = {'project': '1', 'hours_spent': '20'}
    form = TimecardObjectForm(form_data)
    self.assertTrue(form.is_valid())


class TimecardInlineFormSetTests(TestCase):
  fixtures = ['projects/fixtures/projects.json', 'tock/fixtures/dev_user.json']

  def setUp(self):
    self.reporting_period = hours.models.ReportingPeriod.objects.create(
        start_date=datetime.date(2015, 1, 1),
        end_date=datetime.date(2015, 1, 7),
        working_hours=40)
    self.user = get_user_model().objects.get(id=1)
    self.project_1 = projects.models.Project.objects.get(name="openFEC")
    self.project_2 = projects.models.Project.objects.get(name="Peace Corps")
    self.timecard = hours.models.Timecard.objects.create(
        reporting_period=self.reporting_period,
        user=self.user)

  def tearDown(self):
    hours.models.ReportingPeriod.objects.all().delete()
    hours.models.Timecard.objects.all().delete()
    projects.models.Project.objects.all().delete()
    hours.models.TimecardObject.objects.all().delete()

  def form_data(self, clear=[], **kwargs):
    form_data = {
        'timecardobject_set-TOTAL_FORMS': '2',
        'timecardobject_set-INITIAL_FORMS': '0',
        'timecardobject_set-MIN_NUM_FORMS': '',
        'timecardobject_set-MAX_NUM_FORMS': '',
        'timecardobject_set-0-project': '4',
        'timecardobject_set-0-hours_spent': '20',
        'timecardobject_set-1-project': '5',
        'timecardobject_set-1-hours_spent': '20'
    }
    for key in clear:
      del form_data[key]
    for key, value in kwargs.items():
      form_data[key] = value
    return form_data

  def xtest_timecard_inline_formset_valid(self):
    form_data = self.form_data()
    formset = TimecardFormSet(form_data)
    self.assertTrue(formset.is_valid())

  def test_timecard_is_not_100(self):
    form_data = self.form_data()
    form_data['timecardobject_set-2-project'] = '6'
    form_data['timecardobject_set-2-hours_spent'] = '20'
    form_data['timecardobject_set-TOTAL_FORMS'] = '3'
    formset = TimecardFormSet(form_data)
    self.assertFalse(formset.is_valid())
