import datetime

from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token
from employees.models import EmployeeGrade, UserData

from hours.models import (
    ReportingPeriod,
    Timecard,
    TimecardObject
)
from projects.models import Project

class EmployeeGradeTests(TestCase):
    fixtures = ['tock/fixtures/prod_user.json']

    def setUp(self):
        self.employeegrade = EmployeeGrade.objects.create(
            employee=User.objects.get(pk=1),
            grade=8,
            g_start_date=datetime.date.today()
        )
    def test_unique_with_g_start_date(self):
        """Check that multiple EmployeeGrade objects with the same g_start_date
        cannot be saved for the same employee."""
        with self.assertRaises(IntegrityError):
            EmployeeGrade.objects.create(
                employee=User.objects.get(pk=1),
                grade=9,
                g_start_date=datetime.date.today()
            )

    def test_string_method(self):
        """Check that string method override works correctly."""
        expected_string = '{0} - {1} (Starting: {2})'.format(
            self.employeegrade.employee,
            self.employeegrade.grade,
            self.employeegrade.g_start_date
        )

        self.assertEqual(expected_string, str(self.employeegrade))

class UserDataTests(TestCase):
    fixtures = ['projects/fixtures/projects.json']

    def setUp(self):
        # Create regular_user.
        self.regular_user = User.objects.create(
            username='aaron.snow',
            is_superuser=True,
            is_staff=True,
            is_active=True)
        # Create UserData object related to regular_user.
        self.regular_user_userdata = UserData.objects.create(
            user=self.regular_user,
            start_date= datetime.date(2014, 1, 1),
            end_date=datetime.date(2100, 1, 1),
            unit=1,
            is_18f_employee=True,
            current_employee=True
        )
        # Create API token for regular_user.
        self.token = Token.objects.create(user=self.regular_user)

    def test_string_method(self):
        """Check that string method override works correctly."""
        userdata = UserData.objects.get(
            user=self.regular_user
        )
        expected_string = str(userdata.user.username)
        self.assertEqual(expected_string, str(userdata))

    def test_user_data_is_stored(self):
        """ Check that user data was stored correctly """
        userdata = UserData.objects.get(user=self.regular_user)
        self.assertEqual(
            userdata.start_date,
            datetime.date(2014, 1, 1)
        )
        self.assertEqual(
            userdata.end_date,
            datetime.date(2100, 1, 1)
        )
        self.assertEqual(userdata.unit, 1)

    def test_is_late(self):
        """ Check if the user is late when no Timecard is present """
        userdata = UserData.objects.get(user=self.regular_user)
        reporting_period = ReportingPeriod(
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2015, 1, 7),
            exact_working_hours=40,
            min_working_hours=40,
            max_working_hours=60,
            message='This is not a vacation')
        reporting_period.save()
        self.assertEqual(userdata.is_late, True)

    def test_is_not_late(self):
        """ Check if the user is not late when Timecard is present """
        userdata = UserData.objects.get(user=self.regular_user)
        reporting_period = ReportingPeriod.objects.create(
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2015, 1, 7),
            exact_working_hours=40,
            min_working_hours=40,
            max_working_hours=60,
            message='This is not a vacation')
        reporting_period.save()
        timecard = Timecard.objects.create(
            user=self.regular_user,
            reporting_period=reporting_period)
        project = Project.objects.get(name="Platform as a Service")
        timecard.submitted = True
        timecard.save()
        timecard_object_1 = TimecardObject.objects.create(
            timecard=timecard,
            project=project,
            hours_spent=40)

        self.assertEqual(userdata.is_late, False)

    def test_employee_active(self):
        """ Check that the save() method correctly aligns UserData and User
         attributes when current_employee is True."""
        user = User.objects.get(
            username=self.regular_user.username)
        user.is_active = False
        user.save()
        status_before_save = User.objects.get(
            username=self.regular_user.username).is_active
        self.regular_user_userdata.current_employee = True
        self.regular_user_userdata.save()

        status_after_save = User.objects.get(
            username=self.regular_user.username).is_active
        self.assertNotEqual(status_before_save, status_after_save)

    def test_token_is_delete_on_active_is_false(self):
        """ Verify that any tokens associated with a user are deleted when that
        user is marked as not active. """
        token_before_save = self.token
        userdata = UserData.objects.first()
        userdata.current_employee = False
        userdata.save()
        try:
            token_after_save = Token.objects.get(user=self.regular_user)
        except Token.DoesNotExist:
            token_after_save = None
        self.assertNotEqual(token_before_save, token_after_save)
