import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model

import hours.models
import projects.models

from hours.forms import TimecardForm, TimecardObjectForm, TimecardFormSet


class TimecardFormTests(TestCase):
    fixtures = [
        'projects/fixtures/projects.json', 'tock/fixtures/dev_user.json']

    def setUp(self):
        self.reporting_period = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2015, 1, 7),
            working_hours=40)
        self.user = get_user_model().objects.get(id=1)
        self.project_1 = projects.models.Project.objects.get(name="openFEC")
        self.project_2 = projects.models.Project.objects.get(name="Peace Corps")

    def test_valid_form(self):
        form_data = {
            'user': self.user, 'reporting_period': self.reporting_period}
        form = TimecardForm(form_data)
        self.assertTrue(form.is_valid())


class TimecardObjectFormTests(TestCase):
    fixtures = [
        'projects/fixtures/projects.json', 'tock/fixtures/dev_user.json']

    def setUp(self):
        self.reporting_period = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2015, 1, 7),
            working_hours=40)
        self.user = get_user_model().objects.get(id=1)
        self.project_1 = projects.models.Project.objects.get(name="openFEC")
        self.project_2 = projects.models.Project.objects.get(
            name="Peace Corps")

    def test_add_project(self):
        """ Test that existing projects can be added without errors """
        form_data = {'project': '1', 'hours_spent': '20'}
        form = TimecardObjectForm(form_data)
        self.assertTrue(form.is_valid())

    def test_add_wrong_project(self):
        """ Check that missing projects are rejected """
        form_data = {'project': '2323', 'hours_spent': '20'}
        form = TimecardObjectForm(form_data)
        self.assertFalse(form.is_valid())


class TimecardInlineFormSetTests(TestCase):
    fixtures = [
        'projects/fixtures/projects.json', 'tock/fixtures/dev_user.json']

    def setUp(self):
        self.reporting_period = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2015, 1, 7),
            working_hours=40)
        self.user = get_user_model().objects.get(id=1)
        self.project_1 = projects.models.Project.objects.get(name="openFEC")
        self.project_2 = projects.models.Project.objects.get(
            name="Peace Corps")
        self.timecard = hours.models.Timecard.objects.create(
            reporting_period=self.reporting_period,
            user=self.user)

    def form_data(self, clear=[], **kwargs):
        """ Method that auto generates form data for tests """
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

    def test_timecard_inline_formset_valid(self):
        """ Test valid timecard data """
        form_data = self.form_data()
        formset = TimecardFormSet(form_data)
        self.assertTrue(formset.is_valid())

    def test_timecard_is_not_100(self):
        """ Test timecard form data that doesn't total the set working
        hours """
        form_data = self.form_data()
        form_data['timecardobject_set-2-project'] = '6'
        form_data['timecardobject_set-2-hours_spent'] = '20'
        form_data['timecardobject_set-TOTAL_FORMS'] = '3'
        formset = TimecardFormSet(form_data)
        self.assertFalse(formset.is_valid())

    def test_timecard_has_empty_project(self):
        """ Test timecard form data has an empty hours spent value for
        a project """
        form_data = self.form_data()
        form_data['timecardobject_set-2-project'] = '6'
        form_data['timecardobject_set-2-hours_spent'] = None
        form_data['timecardobject_set-TOTAL_FORMS'] = '3'
        formset = TimecardFormSet(form_data)
        self.assertFalse(formset.is_valid())

    def test_timecard_has_0_hours_for_project(self):
        """ Test timecard form data has an 0 hours spent value for
        a project """
        form_data = self.form_data()
        form_data['timecardobject_set-2-project'] = '6'
        form_data['timecardobject_set-2-hours_spent'] = 0
        form_data['timecardobject_set-TOTAL_FORMS'] = '3'
        formset = TimecardFormSet(form_data)
        self.assertFalse(formset.is_valid())

    def test_reporting_period_with_less_than_40_hours(self):
        """ Test the timecard form when the reporting period is less than
        40 hours a week """
        form_data = self.form_data()
        form_data['timecardobject_set-0-hours_spent'] = '8'
        form_data['timecardobject_set-1-hours_spent'] = '8'
        formset = TimecardFormSet(form_data)
        formset.set_working_hours(16)
        self.assertTrue(formset.is_valid())
