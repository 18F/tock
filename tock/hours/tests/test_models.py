from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

import datetime

from hours.models import ReportingPeriod, TimecardObject, Timecard
from projects.models import Project, ProfitLossAccount
from employees.models import EmployeeGrade, UserData


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
        today_utc_day = datetime.datetime.utcnow().day
        self.assertEqual(timecard.created.day, today_utc_day)
        self.assertEqual(timecard.modified.day, today_utc_day)
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
        today_utc_day = datetime.datetime.utcnow().day

        self.assertEqual(timecardobj.created.day, today_utc_day)
        self.assertEqual(timecardobj.modified.day, today_utc_day)

    def test_timecardobject_hours(self):
        """Test the TimeCardObject hours method."""
        self.assertEqual(self.timecard_object_1.hours(), 12)

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
        self.user = User.objects.get_or_create(id=1)
        self.userdata = UserData.objects.create(user=self.user[0])
        self.grade = EmployeeGrade.objects.create(
            employee=self.user[0],
            grade=15,
            g_start_date=datetime.date(2016, 1, 1)
        )
        self.reporting_period = ReportingPeriod.objects.create(
            start_date=datetime.date.today() - datetime.timedelta(days=7),
            end_date=datetime.date.today()
        )
        self.timecard = Timecard.objects.create(
            user=self.user[0],
            reporting_period=self.reporting_period
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
        )

        self.project[0].profit_loss_account = self.pl_acct
        self.project[0].save()

        self.hours_spent = 10

    def test_profit_loss(self):
        """Check that profit / loss codes are correctly appended to
        TimecardObjects."""

        # Test that a valid profit/loss code is appended.
        tco = TimecardObject.objects.create(
            timecard=self.timecard,
            project=self.project[0],
            hours_spent=13
        )
        self.assertEqual(tco.revenue_profit_loss_account, self.pl_acct)

        # After adding invalid profit/loss code, test that the incorrect
        # code is not appended.
        self.project[0].profit_loss_account = self.pl_acct_2
        self.project[0].save()
        tco.save()
        self.assertFalse(tco.revenue_profit_loss_account)

        # Test that a profit / loss code previously appended to a TimecardObject
        # persists when updating the profit / loss code for the project related
        # to the TimecardObject.
        self.project[0].profit_loss_account = self.pl_acct
        self.project[0].save()
        tco_new = TimecardObject.objects.create(
            timecard=self.timecard,
            project=self.project[0],
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
            project=self.project[0],
            hours_spent=self.hours_spent
        )

        self.assertEqual(tco.grade, self.grade)

    def test_correct_grade(self):
        """Checks that latest grade is appended to the timecard object on
        save."""
        new_grade = EmployeeGrade.objects.create(
            employee=self.user[0],
            grade=13,
            g_start_date=datetime.date(2016, 1, 2)
        )
        tco = TimecardObject.objects.create(
            timecard=self.timecard,
            project=self.project[0],
            hours_spent=self.hours_spent
        )

        self.assertEqual(new_grade, tco.grade)

    def test_if_grade_is_none(self):
        """Checks that no grade is appended if no grade exists."""
        EmployeeGrade.objects.filter(employee=self.user[0]).delete()
        tco = TimecardObject.objects.create(
            timecard=self.timecard,
            project=self.project[0],
            hours_spent=self.hours_spent
        )

        self.assertFalse(tco.grade)

    def test_future_grade_only(self):
        """Checks that no grade is appended if the only EmployeeGrade object has
         a g_start_date that is after the end date of the reporting period."""
        EmployeeGrade.objects.filter(employee=self.user[0]).delete()
        newer_grade = EmployeeGrade.objects.create(
            employee=self.user[0],
            grade=13,
            g_start_date=self.reporting_period.end_date + datetime.timedelta(days=1)
        )
        tco = TimecardObject.objects.create(
            timecard=self.timecard,
            project=self.project[0],
            hours_spent=self.hours_spent
        )

        self.assertFalse(tco.grade)
