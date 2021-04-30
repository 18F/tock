import datetime

import hours.models
import projects.models
from django.contrib.auth import get_user_model
from django.test import TestCase, TransactionTestCase
from hours.forms import (TimecardForm, TimecardFormSet, TimecardObjectForm,
                         choice_label_for_project, projects_as_choices)
from organizations.models import Organization, Unit


class TimecardFormTests(TestCase):
    fixtures = [
        'projects/fixtures/projects.json', 'tock/fixtures/prod_user.json',
        'employees/fixtures/user_data.json', 'organizations/fixtures/units.json',
        'organizations/fixtures/organizations.json']

    def setUp(self):
        self.reporting_period = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2015, 1, 7),
            exact_working_hours=40,
            min_working_hours=40,
            max_working_hours=60)
        self.user = get_user_model().objects.first()
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
        project_test = projects.models.Project.objects.first()  # get the first project in the db
        project_test.active = False  # set active field to to false
        project_test.save()  # save change to DB
        data_after_inactive_change = projects_as_choices()
        self.assertNotEqual(data_before_inactive_change, data_after_inactive_change)

    def test_org_and_unit_not_modifiable(self):
        """Organization and unit are unchanged when saving a bound form instance"""
        org = Organization.objects.first()
        unit = Unit.objects.first()
        user_data = self.user.user_data
        user_data.organization = org
        user_data.unit = unit
        user_data.save()

        timecard = hours.models.Timecard.objects.create(user=self.user, reporting_period=self.reporting_period)

        form_data = {'user': self.user, 'reporting_period': self.reporting_period}
        TimecardForm(form_data, instance=timecard).save()
        timecard.refresh_from_db()
        self.assertEqual(org, timecard.organization)
        self.assertEqual(unit, timecard.unit)


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


def time_card_inlineformset_setup(self):
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

    self.initial_form_data = {
     'timecardobjects-TOTAL_FORMS': '2',
            'timecardobjects-INITIAL_FORMS': '0',
            'timecardobjects-MIN_NUM_FORMS': '',
            'timecardobjects-MAX_NUM_FORMS': '',
            'timecardobjects-0-project': '4',
            'timecardobjects-0-hours_spent': '20',
            'timecardobjects-1-project': '5',
            'timecardobjects-1-hours_spent': '20'
    }


class TimecardInlineFormSetTransactionTests(TransactionTestCase):
    fixtures = [
     'projects/fixtures/projects.json', 'tock/fixtures/prod_user.json',
            'employees/fixtures/user_data.json'
    ]

    setUp = time_card_inlineformset_setup

    def test_timecard_inline_formset_modify_saved(self):
        """Users can swap project IDs between TimeCardObjects """
        form_data = self.initial_form_data
        formset = TimecardFormSet(form_data, instance=self.timecard)
        # Save these timecard entries for later modification
        formset.save_only = True
        formset.is_valid()
        formset.save()

        # We've got a saved timecard, lets try to edit it by swapping the projects
        project5 = self.timecard.timecardobjects.get(project_id=5)
        project4 = self.timecard.timecardobjects.get(project_id=4)
        form_data.update({'timecardobjects-0-id': project4.id,
                          'timecardobjects-1-id': project5.id,
                          'timecardobjects-0-project': '5',
                          'timecardobjects-1-project': '4',
                          'timecardobjects-INITIAL_FORMS': '2'})
        formset = TimecardFormSet(form_data, instance=self.timecard)
        formset.is_valid()
        formset.save()

class TimecardInlineFormSetTests(TestCase):
    fixtures = [
        'projects/fixtures/projects.json', 'tock/fixtures/prod_user.json',
        'employees/fixtures/user_data.json']

    setUp = time_card_inlineformset_setup

    def form_data(self, clear=[], **kwargs):
        """ Method that auto generates form data for tests """
        form_data = self.initial_form_data
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
        form_data['timecardobjects-2-project'] = '6'
        form_data['timecardobjects-2-hours_spent'] = '50'
        form_data['timecardobjects-TOTAL_FORMS'] = '3'
        formset = TimecardFormSet(form_data)
        self.assertFalse(formset.is_valid())

    def test_timecard_is_too_small(self):
        """ Test timecard form data that is smaller than the minimum
        allowable hours """
        form_data = self.form_data()
        form_data['timecardobjects-1-project'] = '6'
        form_data['timecardobjects-1-hours_spent'] = '10'
        form_data['timecardobjects-TOTAL_FORMS'] = '2'
        formset = TimecardFormSet(form_data)
        self.assertFalse(formset.is_valid())

    def test_aws_timecard_is_wrong_size(self):
        """ Test timecard form data does not abide by min/max hours if
        user is alternative work schedule eligible. """
        # Too small.
        form_data = self.form_data()
        form_data['timecardobjects-1-project'] = '6'
        form_data['timecardobjects-1-hours_spent'] = '10'
        form_data['timecardobjects-TOTAL_FORMS'] = '2'
        formset = TimecardFormSet(form_data)
        formset.aws_eligible = True
        self.assertTrue(formset.is_valid())
        # Too large
        form_data = self.form_data()
        form_data['timecardobjects-1-project'] = '6'
        form_data['timecardobjects-1-hours_spent'] = '50'
        form_data['timecardobjects-TOTAL_FORMS'] = '2'
        formset = TimecardFormSet(form_data)
        formset.aws_eligible = True
        self.assertTrue(formset.is_valid())

    def test_timecard_has_empty_project(self):
        """ Test timecard form data has an empty hours spent value for
        a project """
        form_data = self.form_data()
        form_data['timecardobjects-2-project'] = '6'
        form_data['timecardobjects-2-hours_spent'] = None
        form_data['timecardobjects-TOTAL_FORMS'] = '3'
        formset = TimecardFormSet(form_data)
        self.assertTrue(formset.is_valid())

    def test_timecard_has_0_hours_for_project(self):
        """ Test timecard form data has an 0 hours spent value for
        a project """
        form_data = self.form_data()
        form_data['timecardobjects-2-project'] = '6'
        form_data['timecardobjects-2-hours_spent'] = 0
        form_data['timecardobjects-TOTAL_FORMS'] = '3'
        formset = TimecardFormSet(form_data)
        self.assertTrue(formset.is_valid())

    def test_no_zero_hours_saved(self):
        """Tests that TimecardObject's with None or 0 hours are not entered
        into the database on form submission."""
        form_data = {
            'timecardobjects-TOTAL_FORMS': '1',
            'timecardobjects-INITIAL_FORMS': '0',
            'timecardobjects-MIN_NUM_FORMS': '',
            'timecardobjects-MAX_NUM_FORMS': '',
            'timecardobjects-0-project': '4',
            'timecardobjects-0-hours_spent': ''
        }
        formset = TimecardFormSet(form_data)
        formset.is_valid()
        self.assertTrue(formset[0].cleaned_data['DELETE'])

    def test_reporting_period_with_less_than_min_hours_success(self):
        """ Test the timecard form when the reporting period requires at least
        16 hours to be reported and the hours entered are less than 16"""
        form_data = self.form_data()
        form_data['timecardobjects-0-hours_spent'] = '8'
        form_data['timecardobjects-1-hours_spent'] = '10'
        formset = TimecardFormSet(form_data)
        formset.set_min_working_hours(16)
        self.assertTrue(formset.is_valid())

    def test_reporting_period_with_less_than_min_hours_failure(self):
        """ Test the timecard form when the reporting period requires at least
        16 hours to be reported and the hours entered are less than 16"""
        form_data = self.form_data()
        form_data['timecardobjects-0-hours_spent'] = '5'
        form_data['timecardobjects-1-hours_spent'] = '5'
        formset = TimecardFormSet(form_data)
        formset.set_min_working_hours(16)
        self.assertFalse(formset.is_valid())

    def test_reporting_period_with_more_than_max_hours_success(self):
        """ Test the timecard form when the reporting period requires no more
        than 60 hours to be reported and the hours entered are less than 60"""
        form_data = self.form_data()
        form_data['timecardobjects-0-hours_spent'] = '50'
        form_data['timecardobjects-1-hours_spent'] = '2'
        formset = TimecardFormSet(form_data)
        formset.set_max_working_hours(60)
        self.assertTrue(formset.is_valid())

    def test_reporting_period_with_more_than_max_hours_failure(self):
        """ Test the timecard form when the reporting period requires no more
        than 60 hours to be reported and the hours entered are more than 60"""
        form_data = self.form_data()
        form_data['timecardobjects-0-hours_spent'] = '50'
        form_data['timecardobjects-1-hours_spent'] = '20'
        formset = TimecardFormSet(form_data)
        formset.set_max_working_hours(60)
        self.assertFalse(formset.is_valid())


    def test_reporting_period_with_less_than_min_hours_success_save_mode(self):
        """ Test the timecard form when the reporting period is less than
        minimum required hours a period and you save (not submit) """
        form_data = self.form_data()
        form_data['timecardobjects-0-hours_spent'] = '5'
        form_data['timecardobjects-1-hours_spent'] = '5'
        formset = TimecardFormSet(form_data)
        formset.set_min_working_hours(16)
        formset.save_only = True
        self.assertTrue(formset.is_valid())

    def test_one_project_with_notes_and_one_without_notes_is_invalid(self):
        """ Test the timecard form when one entry requires notes and another
        entry does not, and the notes are not filled in"""
        form_data = self.form_data()
        form_data['timecardobjects-0-project'] = '2'
        formset = TimecardFormSet(form_data)
        self.assertFalse(formset.is_valid())

    def test_one_project_with_notes_and_one_without_notes_is_valid(self):
        """ Test the timecard form when one entry requires notes and another
        entry does not, and the notes are filled in"""
        form_data = self.form_data()
        form_data['timecardobjects-0-project'] = '2'
        form_data['timecardobjects-0-notes'] = 'Did some work.'
        formset = TimecardFormSet(form_data)
        self.assertTrue(formset.is_valid())
