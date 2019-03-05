from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

import datetime

from hours.models import (
    HolidayPrefills,
    ReportingPeriod,
    Timecard,
    TimecardNote,
    TimecardObject
)
from projects.models import Project, ProfitLossAccount
from employees.models import EmployeeGrade, UserData


class HolidayPrefillsTests(TestCase):
    fixtures = ['projects/fixtures/projects.json',]
    def setUp(self):
        self.holiday_prefills = HolidayPrefills.objects.create(
            project=Project.objects.first(),
            hours_per_period=8
        )

    def test_string_method(self):
        """Tests custom string method returns correct string"""
        expected_string = '{} ({} hrs.)'.format(
            self.holiday_prefills.project.name,
            self.holiday_prefills.hours_per_period
        )
        self.assertEqual(expected_string, self.holiday_prefills.__str__())

class ReportingPeriodTests(TestCase):
    def setUp(self):
        self.reporting_period = ReportingPeriod(
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2015, 1, 7),
            exact_working_hours=40,
            min_working_hours=40,
            max_working_hours=60,
            message='This is not a vacation')
        self.reporting_period.save()

    def test_reporting_period_save(self):
        """Ensure that data was saved properly."""
        reporting_period = ReportingPeriod.objects.first()
        self.assertEqual(40, reporting_period.exact_working_hours)
        self.assertEqual(
            datetime.date(2015, 1, 1), reporting_period.start_date)
        self.assertEqual(datetime.date(2015, 1, 7), reporting_period.end_date)
        self.assertEqual('This is not a vacation', reporting_period.message)
        self.assertEqual(40, reporting_period.min_working_hours)
        self.assertEqual(60, reporting_period.max_working_hours)

    def test_unique_constraint(self):
        """ Check that unique constrains work for reporting period."""
        with self.assertRaises(ValidationError):
            ReportingPeriod(
                start_date=datetime.date(2015, 1, 1),
                end_date=datetime.date(2015, 1, 7),
                exact_working_hours=40).save()

    def test_get_fiscal_year(self):
        """Check to ensure the proper fiscal year is returned."""
        self.assertEqual(2015, self.reporting_period.get_fiscal_year())
        reporting_period_2 = ReportingPeriod(
            start_date=datetime.date(2015, 10, 31),
            end_date=datetime.date(2015, 11, 7),
            exact_working_hours=32)
        self.assertEqual(2016, reporting_period_2.get_fiscal_year())

        # Testing the week that spans two FYs
        reporting_period_3 = ReportingPeriod(
            start_date=datetime.date(2014, 9, 28),
            end_date=datetime.date(2014, 10, 4),
            exact_working_hours=32)
        self.assertEqual(2015, reporting_period_3.get_fiscal_year())
        reporting_period_4 = ReportingPeriod(
            start_date=datetime.date(2015, 9, 27),
            end_date=datetime.date(2015, 10, 3),
            exact_working_hours=32)
        self.assertEqual(2015, reporting_period_4.get_fiscal_year())

    def test_get_fiscal_year_start_date(self):
        # test more October date than September date
        self.assertEqual(datetime.date(2014, 9, 28),
            ReportingPeriod.get_fiscal_year_start_date(2015))
        # test more September date than October date
        self.assertEqual(datetime.date(2015, 10, 4),
            ReportingPeriod.get_fiscal_year_start_date(2016))
        # test fiscal year starts right on 10/1
        self.assertEqual(datetime.date(2017, 10, 1),
            ReportingPeriod.get_fiscal_year_start_date(2018))

    def test_get_fiscal_year_end_date(self):
        # test more October date than September date
        self.assertEqual(datetime.date(2014, 9, 27),
            ReportingPeriod.get_fiscal_year_end_date(2014))
        # test more September date than October date
        self.assertEqual(datetime.date(2015, 10, 3),
            ReportingPeriod.get_fiscal_year_end_date(2015))
        # test fiscal year ends right on 9/30
        self.assertEqual(datetime.date(2017, 9, 30),
            ReportingPeriod.get_fiscal_year_end_date(2017))


class TimecardTests(TestCase):
    fixtures = [
        'projects/fixtures/projects.json',
        'tock/fixtures/prod_user.json'
    ]

    def setUp(self):
        self.reporting_period = ReportingPeriod.objects.create(
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2015, 1, 7),
            exact_working_hours=40)
        self.reporting_period.save()
        self.user = get_user_model().objects.get(id=1)
        self.userdata = UserData.objects.create(user=self.user)
        self.timecard = Timecard.objects.create(
            user=self.user,
            reporting_period=self.reporting_period)
        self.project_1 = Project.objects.get(name="openFEC")
        self.project_2 = Project.objects.get(
            name="Peace Corps")
        self.timecard_object_1 = TimecardObject.objects.create(
            timecard=self.timecard,
            project=self.project_1,
            hours_spent=12)
        self.timecard_object_2 = TimecardObject.objects.create(
            timecard=self.timecard,
            project=self.project_2,
            hours_spent=28)

    def test_time_card_saved(self):
        """Test that the time card was saved correctly."""
        timecard = Timecard.objects.first()
        self.assertEqual(timecard.user.pk, 1)
        self.assertEqual(timecard.reporting_period.exact_working_hours, 40)
        self.assertEqual(timecard.created.day, datetime.datetime.utcnow().day)
        self.assertEqual(timecard.modified.day, datetime.datetime.utcnow().day)
        self.assertEqual(len(timecard.time_spent.all()), 2)

    def test_time_card_unique_constraint(self):
        """Test that the time card model is constrained by user and reporting
        period."""
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                # Prevents django.db.transaction.TransactionManagementError
                Timecard.objects.create(
                    user=self.user,
                    reporting_period=self.reporting_period).save()

    def test_timecard_string_return(self):
        """Ensure the returned string for the timecard is as expected."""
        self.assertEqual('aaron.snow - 2015-01-01', str(self.timecard))

    def test_timecardobject_saved(self):
        """Check that TimeCardObject was saved properly."""
        timecardobj = TimecardObject.objects.get(
            pk=self.timecard_object_1.pk
        )
        self.assertEqual(timecardobj.timecard.user.pk, 1)
        self.assertEqual(timecardobj.project.name, 'openFEC')
        self.assertEqual(timecardobj.hours_spent, 12)
        self.assertEqual(timecardobj.created.day, datetime.datetime.utcnow().day)
        self.assertEqual(timecardobj.modified.day, datetime.datetime.utcnow().day)

    def test_timecardobject_hours(self):
        """Test the TimeCardObject hours method."""
        self.assertEqual(self.timecard_object_1.hours(), 12)


class TimecardNoteTests(TestCase):
    def setUp(self):
        # Ensure that we are dealing with just the two timecard note objects
        # that we plan on testing.
        TimecardNote.objects.all().delete()

        self.timecard_note_enabled = TimecardNote(
            title='Enabled test note',
            body='This is a test note that is enabled.'
        )
        self.timecard_note_enabled.save()

        self.timecard_note_disabled = TimecardNote(
            title='Disabled test note',
            body='This is a test note that is disabled.',
            enabled=False
        )
        self.timecard_note_disabled.save()

    def test_get_only_enabled_timecard_notes(self):
        """Ensure that we are only returning enabled timecard notes."""
        enabled_timecard_notes = TimecardNote.objects.enabled()
        self.assertEqual(enabled_timecard_notes.count(), 1)
        self.assertEqual(
            enabled_timecard_notes.last(),
            self.timecard_note_enabled
        )

    def test_get_only_disabled_timecard_notes(self):
        """Ensure that we are only returning disabled timecard notes."""
        disabled_timecard_notes = TimecardNote.objects.disabled()
        self.assertEqual(disabled_timecard_notes.count(), 1)
        self.assertEqual(
            disabled_timecard_notes.first(),
            self.timecard_note_disabled
        )

    def test_timecard_note_default_order(self):
        """Tests the default ordering of the timecard notes."""

        timecard_notes = TimecardNote.objects.all()
        self.assertEqual(
            timecard_notes[0].position,
            self.timecard_note_enabled.position
        )
        self.assertEqual(
            timecard_notes[1].position,
            self.timecard_note_disabled.position
        )

    def test_timecard_note_changed_order(self):
        """Tests the changed ordering of the timecard notes."""

        self.timecard_note_enabled.position = 2
        self.timecard_note_enabled.save()
        self.timecard_note_disabled.position = 1
        self.timecard_note_disabled.save()

        timecard_notes = TimecardNote.objects.all()
        self.assertEqual(
            timecard_notes[0].position,
            self.timecard_note_disabled.position
        )
        self.assertEqual(
            timecard_notes[1].position,
            self.timecard_note_enabled.position
        )


class TimecardObjectTests(TestCase):
    fixtures = [
        'tock/fixtures/prod_user.json',
        'projects/fixtures/projects.json',
        'hours/fixtures/timecards.json',
    ]
    def setUp(self):
        """Set up includes deletion of all existing timecards loaded from
        fixtures to eliminate the possibility of a unique_together error."""
        Timecard.objects.filter().delete()
        self.user = User.objects.get_or_create(id=1)[0]
        self.userdata = UserData.objects.create(user=self.user)
        self.grade = EmployeeGrade.objects.create(
            employee=self.user,
            grade=15,
            g_start_date=datetime.date(2016, 1, 1)
        )
        self.reporting_period = ReportingPeriod.objects.create(
            start_date=datetime.date.today() - datetime.timedelta(days=14),
            end_date=datetime.date.today() - datetime.timedelta(days=7)
        )
        self.reporting_period2 = ReportingPeriod.objects.create(
            start_date=datetime.date.today() - datetime.timedelta(days=7),
            end_date=datetime.date.today()
        )
        self.timecard = Timecard.objects.create(
            user=self.user,
            reporting_period=self.reporting_period
        )
        self.timecard2 = Timecard.objects.create(
            user=self.user,
            reporting_period=self.reporting_period2
        )
        self.pl_acct = ProfitLossAccount.objects.create(
            name='PL',
            accounting_string='string',
            as_start_date=datetime.date.today() - datetime.timedelta(days=10),
            as_end_date=datetime.date.today() + datetime.timedelta(days=355),
            account_type='Revenue'
        )
        self.pl_acct_2 = ProfitLossAccount.objects.create(
            name='PL2',
            accounting_string='newstring',
            as_start_date=datetime.date.today() + datetime.timedelta(days=10),
            as_end_date=datetime.date.today() - datetime.timedelta(days=10),
            account_type='Expense'
        )
        self.pl_acct_3 = ProfitLossAccount.objects.create(
            name='PL3',
            accounting_string='newstring',
            as_start_date=datetime.date.today() - datetime.timedelta(days=10),
            as_end_date=datetime.date.today() + datetime.timedelta(days=355),
            account_type='Expense'
        )

        self.project = Project.objects.get_or_create(
            pk=1
        )[0]

        self.project.profit_loss_account = self.pl_acct
        self.project.save()

        self.hours_spent = 10

    def test_profit_loss(self):
        """Check that profit / loss codes are correctly appended to
        TimecardObjects."""

        # Test that a valid profit/loss code is appended.
        tco = TimecardObject.objects.create(
            timecard=self.timecard,
            project=self.project,
            hours_spent=13
        )
        self.assertEqual(tco.revenue_profit_loss_account, self.pl_acct)

        # After adding invalid profit/loss code, test that the incorrect
        # code is not appended.
        self.project.profit_loss_account = self.pl_acct_2
        self.project.save()
        tco.save()
        self.assertFalse(tco.revenue_profit_loss_account)

        # Test that a profit / loss code previously appended to a TimecardObject
        # persists when updating the profit / loss code for the project related
        # to the TimecardObject.
        self.project.profit_loss_account = self.pl_acct
        self.project.save()
        tco_new = TimecardObject.objects.create(
            timecard=self.timecard2,
            project=self.project,
            hours_spent=11
        )
        self.assertNotEqual(
            tco.revenue_profit_loss_account,
            tco_new.revenue_profit_loss_account
        )
        # Test that a correct profit / loss code will be appended to
        # expense_profit_loss_account from UserData.
        self.userdata.profit_loss_account = self.pl_acct_3
        self.userdata.save()
        tco.save()
        self.assertEqual(tco.expense_profit_loss_account, self.pl_acct_3)

        # Test that an incorrect profit / loss code will not be appended to
        # expense_profit_loss_account.
        self.userdata.profit_loss_account = self.pl_acct
        self.userdata.save()
        tco.save()
        self.assertFalse(tco.expense_profit_loss_account)

    def test_employee_grade(self):
        """Checks that employee grade is appended to timecard object on save."""
        tco = TimecardObject.objects.create(
            timecard=self.timecard,
            project=self.project,
            hours_spent=self.hours_spent
        )

        self.assertEqual(tco.grade, self.grade)

    def test_correct_grade(self):
        """Checks that latest grade is appended to the timecard object on
        save."""
        new_grade = EmployeeGrade.objects.create(
            employee=self.user,
            grade=13,
            g_start_date=datetime.date(2016, 1, 2)
        )
        tco = TimecardObject.objects.create(
            timecard=self.timecard,
            project=self.project,
            hours_spent=self.hours_spent
        )

        self.assertEqual(new_grade, tco.grade)

    def test_if_grade_is_none(self):
        """Checks that no grade is appended if no grade exists."""
        EmployeeGrade.objects.filter(employee=self.user).delete()
        tco = TimecardObject.objects.create(
            timecard=self.timecard,
            project=self.project,
            hours_spent=self.hours_spent
        )

        self.assertFalse(tco.grade)

    def test_future_grade_only(self):
        """Checks that no grade is appended if the only EmployeeGrade object has
         a g_start_date that is after the end date of the reporting period."""
        EmployeeGrade.objects.filter(employee=self.user).delete()
        EmployeeGrade.objects.create(
            employee=self.user,
            grade=13,
            g_start_date=self.reporting_period.end_date + datetime.timedelta(days=1)
        )
        tco = TimecardObject.objects.create(
            timecard=self.timecard,
            project=self.project,
            hours_spent=self.hours_spent
        )

        self.assertFalse(tco.grade)


class ProjectTests(TestCase):
    fixtures = [
        'projects/fixtures/projects.json',
    ]

    def setUp(self):
        self.project_1 = Project.objects.get(name='openFEC')
        self.project_2 = Project.objects.get(name='Peace Corps')

        self.project_1.active = False
        self.project_2.active = False

        self.project_1.save()
        self.project_2.save()

    def test_active_projects_model_manager(self):
        """Test that only active projects are returned by the active() model
        manager method."""

        projects = list(Project.objects.active())
        project_count = len(projects)
        total_project_count = Project.objects.count()

        self.assertNotIn(self.project_1, projects)
        self.assertNotIn(self.project_2, projects)
        self.assertEqual(project_count, total_project_count - 2)

    def test_inactive_projects_model_manager(self):
        """Test that only active projects are returned by the active() model
        manager method."""

        projects = list(Project.objects.inactive())
        project_count = len(projects)
        total_project_count = Project.objects.count()

        self.assertIn(self.project_1, projects)
        self.assertIn(self.project_2, projects)
        self.assertEqual(project_count, 2)
        self.assertNotEqual(project_count, total_project_count)
