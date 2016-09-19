import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model

import hours.models
import projects.models

from hours.forms import (
    TimecardForm, TimecardObjectForm,
    TimecardFormSet, projects_as_choices,
    choice_label_for_project
)


class TimecardFormTests(TestCase):
    fixtures = [
        'projects/fixtures/projects.json', 'tock/fixtures/prod_user.json']

    def setUp(self):
        self.reporting_period = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2015, 1, 7),
            exact_working_hours=40,
            min_working_hours=40,
            max_working_hours=60)
        self.user = get_user_model().objects.get(id=1)
        self.project_1 = projects.models.Project.objects.get(name="openFEC")
        self.project_2 = projects.models.Project.objects.get(name="Peace Corps")
        self.project_3 = projects.models.Project.objects.get(name="General")

    def test_valid_form(self):
        form_data = {
            'user': self.user, 'reporting_period': self.reporting_period}
        form = TimecardForm(form_data)
        self.assertTrue(form.is_valid())

    def test_choice_label_for_project(self):
        self.assertEqual(choice_label_for_project(self.project_1),
                         '32 - openFEC')

    def test_projects_as_choices(self):
        """tests projects_as_choices only returns projects marked active:
        (1) mark a project as inactive;
        (2) look for that project inside projects_as_choices;
        (3) test should fail if it finds the project"""
        data_before_inactive_change = projects_as_choices()
        project_test = projects.models.Project.objects.first() #get the first project in the db
        project_test.active = False #set active field to to false
        project_test.save() #save change to DB
        data_after_inactive_change = projects_as_choices()
        self.assertNotEqual(data_before_inactive_change, data_after_inactive_change)


class TimecardObjectFormTests(TestCase):
    fixtures = [
        'projects/fixtures/projects.json', 'tock/fixtures/prod_user.json']

    def setUp(self):
        self.reporting_period = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2015, 1, 7),
            exact_working_hours=40,
            min_working_hours=40,
            max_working_hours=60
            )
        self.user = get_user_model().objects.get(id=1)
        self.project_1 = projects.models.Project.objects.get(name="openFEC")
        self.project_2 = projects.models.Project.objects.get(
            name="Peace Corps")
        self.project_3 = projects.models.Project.objects.get(name='General')
        self.project_3.notes_displayed = True
        self.project_3.notes_required = True
        self.project_3.save()

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

    def test_general_has_required_notes_field(self):
        """tests that a timecard object with a General entry that is missing an
        accompaning blank notes field is not valid"""
        form_data = {'project': '2', 'hours_spent': '40'}
        form = TimecardObjectForm(form_data)
        self.assertFalse(form.is_valid())

    def test_blank_hrs(self):
        """blank/null hrs become 0"""
        form_data = {
            'project': '2',
            'hours_spent': None,
        }

        form = TimecardObjectForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.cleaned_data['hours_spent'], 0)

    def test_general_notes_field_strips_html(self):
        """tests that a timecard object with a notes field that has HTML in it
        strips the HTML before saving."""
        form_data = {
            'project': '2',
            'hours_spent': '40',
            'notes': '<strong>This is a <em>test</em>!</strong>'
        }

        form = TimecardObjectForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['notes'], 'This is a test!')

class TimecardInlineFormSetTests(TestCase):
    fixtures = [
        'projects/fixtures/projects.json', 'tock/fixtures/prod_user.json']

    def setUp(self):
        self.reporting_period = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2015, 1, 7),
            exact_working_hours=40,
            min_working_hours=40,
            max_working_hours=60
            )
        self.user = get_user_model().objects.get(id=1)
        self.project_1 = projects.models.Project.objects.get(name="openFEC")
        self.project_2 = projects.models.Project.objects.get(
            name="Peace Corps")
        self.project_3 = projects.models.Project.objects.get(name='General')
        self.project_3.notes_displayed = True
        self.project_3.notes_required = True
        self.project_3.save()
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
            'timecardobject_set-0-hours_spent': '22',
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

    def test_timecard_inline_formset_save_only(self):
        """ Test formset's save_only field """
        form_data = self.form_data()
        formset = TimecardFormSet(form_data)
        self.assertFalse(formset.save_only)  # default
        formset.save_only = True
        self.assertTrue(formset.save_only)

    def test_timecard_is_too_big(self):
        """ Test timecard form data that exceeds the maximum hours allowed """
        form_data = self.form_data()
        form_data['timecardobject_set-2-project'] = '6'
        form_data['timecardobject_set-2-hours_spent'] = '50'
        form_data['timecardobject_set-TOTAL_FORMS'] = '3'
        formset = TimecardFormSet(form_data)
        self.assertFalse(formset.is_valid())

    def test_timecard_is_too_small(self):
        """ Test timecard form data that is smaller than the minimum
        allowable hours """
        form_data = self.form_data()
        form_data['timecardobject_set-1-project'] = '6'
        form_data['timecardobject_set-1-hours_spent'] = '10'
        form_data['timecardobject_set-TOTAL_FORMS'] = '2'
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
        self.assertTrue(formset.is_valid())

    def test_timecard_has_0_hours_for_project(self):
        """ Test timecard form data has an 0 hours spent value for
        a project """
        form_data = self.form_data()
        form_data['timecardobject_set-2-project'] = '6'
        form_data['timecardobject_set-2-hours_spent'] = 0
        form_data['timecardobject_set-TOTAL_FORMS'] = '3'
        formset = TimecardFormSet(form_data)
        self.assertTrue(formset.is_valid())

    def test_reporting_period_with_less_than_min_hours_success(self):
        """ Test the timecard form when the reporting period requires at least
        16 hours to be reported and the hours entered are less than 16"""
        form_data = self.form_data()
        form_data['timecardobject_set-0-hours_spent'] = '8'
        form_data['timecardobject_set-1-hours_spent'] = '10'
        formset = TimecardFormSet(form_data)
        formset.set_min_working_hours(16)
        self.assertTrue(formset.is_valid())

    def test_reporting_period_with_less_than_min_hours_failure(self):
        """ Test the timecard form when the reporting period requires at least
        16 hours to be reported and the hours entered are less than 16"""
        form_data = self.form_data()
        form_data['timecardobject_set-0-hours_spent'] = '5'
        form_data['timecardobject_set-1-hours_spent'] = '5'
        formset = TimecardFormSet(form_data)
        formset.set_min_working_hours(16)
        self.assertFalse(formset.is_valid())

    def test_reporting_period_with_more_than_max_hours_success(self):
        """ Test the timecard form when the reporting period requires no more
        than 60 hours to be reported and the hours entered are less than 60"""
        form_data = self.form_data()
        form_data['timecardobject_set-0-hours_spent'] = '50'
        form_data['timecardobject_set-1-hours_spent'] = '2'
        formset = TimecardFormSet(form_data)
        formset.set_max_working_hours(60)
        self.assertTrue(formset.is_valid())

    def test_reporting_period_with_more_than_max_hours_failure(self):
        """ Test the timecard form when the reporting period requires no more
        than 60 hours to be reported and the hours entered are more than 60"""
        form_data = self.form_data()
        form_data['timecardobject_set-0-hours_spent'] = '50'
        form_data['timecardobject_set-1-hours_spent'] = '20'
        formset = TimecardFormSet(form_data)
        formset.set_max_working_hours(60)
        self.assertFalse(formset.is_valid())


    def test_reporting_period_with_less_than_min_hours_success_save_mode(self):
        """ Test the timecard form when the reporting period is less than
        minimum required hours a period and you save (not submit) """
        form_data = self.form_data()
        form_data['timecardobject_set-0-hours_spent'] = '5'
        form_data['timecardobject_set-1-hours_spent'] = '5'
        formset = TimecardFormSet(form_data)
        formset.set_min_working_hours(16)
        formset.save_only = True
        self.assertTrue(formset.is_valid())

    def test_one_project_with_notes_and_one_without_notes_is_invalid(self):
        """ Test the timecard form when one entry requires notes and another
        entry does not, and the notes are not filled in"""
        form_data = self.form_data()
        form_data['timecardobject_set-0-project'] = '2'
        formset = TimecardFormSet(form_data)
        self.assertFalse(formset.is_valid())

    def test_one_project_with_notes_and_one_without_notes_is_valid(self):
        """ Test the timecard form when one entry requires notes and another
        entry does not, and the notes are filled in"""
        form_data = self.form_data()
        form_data['timecardobject_set-0-project'] = '2'
        form_data['timecardobject_set-0-notes'] = 'Did some work.'
        formset = TimecardFormSet(form_data)
        self.assertTrue(formset.is_valid())
