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
	def test_reporting_period_save(self):
		reporting_period = hours.models.ReportingPeriod(
				start_date=datetime.date(2015, 1, 1),
				end_date=datetime.date(2015, 1, 7),
				working_hours=32)
		reporting_period.save()

		retrieved = hours.models.ReportingPeriod.objects.get(
			pk=reporting_period.pk)

		self.assertEqual('2015-01-01', str(retrieved))
		self.assertEqual(32, retrieved.working_hours)

	def test_max_reporting_period_length(self):
		"""Check to ensure a reporting period cannot be longer than 40 hours"""
		with self.assertRaises(ValidationError):
			hours.models.ReportingPeriod(
				start_date=datetime.date(2015, 1, 1),
				end_date=datetime.date(2015, 1, 7),
				working_hours=45).save()

class TimecardTests(TestCase):
	fixtures = ['projects.json', 'dev_user.json']

	def setUp(self):
		self.reporting_period = hours.models.ReportingPeriod.objects.create(
				start_date=datetime.date(2015, 1, 1),
				end_date=datetime.date(2015, 1, 7),
				working_hours=40)
		self.timecard = hours.models.Timecard.objects.create(
			user=self.user,
			reporting_period=self.reporting_period)
		self.project_1 = projects.models.Project.objects.get(name="openFEC")
		self.project_2 = projects.models.Project.objects.get(name="Peace Corps")
		self.timecard_object_1 = hours.models.TimecardObject.objects.create(
			timecard = self.timecard,
			project = self.project_1,
			time_percentage=30)
		self.timecard_object_2 = hours.models.TimecardObject.objects.create(
			timecard = self.timecard,
			project = self.project_2,
			time_percentage=70)
		self.timecard_object_2 
	def test_timecard_string_return(self):
		
		timecard


