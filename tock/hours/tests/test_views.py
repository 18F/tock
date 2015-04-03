import os
import shutil
from unittest.mock import Mock, patch
import datetime
import csv

from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.conf import settings
from django.test import TestCase
from django.contrib.auth import get_user_model

import hours.models
import projects.models
import hours.utils
import hours.views

class UtilTests(TestCase):

	def test_number_of_hours_util(self):
		"""Ensure the number of hours returns a correct value"""
		self.assertEqual(20, hours.utils.number_of_hours(50, 40))

class ReportTests(TestCase):
	fixtures = [
		'projects/fixtures/projects.json',
		'tock/fixtures/dev_user.json'
	]

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
			timecard = self.timecard,
			project = self.project_1,
			time_percentage=30)
		self.timecard_object_2 = hours.models.TimecardObject.objects.create(
			timecard = self.timecard,
			project = self.project_2,
			time_percentage=70)

	def tearDown(self):
		hours.models.ReportingPeriod.objects.all().delete()
		hours.models.Timecard.objects.all().delete()
		projects.models.Project.objects.all().delete()
		hours.models.TimecardObject.objects.all().delete()

	def test_ReportList_get_queryset(self):
		reporting_period_2 = hours.models.ReportingPeriod.objects.create(
				start_date=datetime.date(2016, 1, 1),
				end_date=datetime.date(2016, 1, 7),
				working_hours=40)

		request = 'fake request'
		response = self.client.get(reverse('ListReports'))
		response = response.content.decode('utf-8')
		self.assertTrue(response.index('2016') < response.index('2015'))

	def test_TimecardCSVView(self):
		request = 'fake request'
		response = hours.views.TimecardCSVView(request, "2015-01-01").content.decode('utf-8').splitlines()[2]
		self.assertEqual('2015-01-01 - 2015-01-07,testuser@gsa.gov,Peace Corps,70%,28.0', response)
	