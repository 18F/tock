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

from hours.forms import TimecardFormSet

class TimecardFormTests(TestCase):
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
        self.project_1 = projects.models.Project.objects.get(name="openFEC")
        self.project_2 = projects.models.Project.objects.get(name="Peace Corps")


    def tearDown(self):
        hours.models.ReportingPeriod.objects.all().delete()
        hours.models.Timecard.objects.all().delete()
        projects.models.Project.objects.all().delete()
        hours.models.TimecardObject.objects.all().delete()

    def form_data(self, clear=[], **kwargs):
        form_data = {
            'timecardobject_set-TOTAL_FORMS': '3',
            'timecardobject_set-INITIAL_FORMS': '2',
            'timecardobject_set-MIN_NUM_FORMS': '0',
            'timecardobject_set-MAX_NUM_FORMS': '1000',
            'timecardobject_set-0-project': '4',
            'timecardobject_set-0-time_percentage': '50',
            'timecardobject_set-0-timecard': '1',
            'timecardobject_set-0-id': '1',
            'timecardobject_set-1-project': '5',
            'timecardobject_set-1-time_percentage': '50',
            'timecardobject_set-1-timecard': '1',
            'timecardobject_set-1-id': '2',
        }
        for key in clear:
            del form_data[key]
        for key, value in kwargs.items():
            form_data[key] = value
        return form_data