import datetime

from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token

from employees.models import EmployeeGrade, UserData
from hours.models import ReportingPeriod, Timecard, TimecardObject
from projects.models import Project

class EmployeeGradeTests(TestCase):
    fixtures = [
        'tock/fixtures/prod_user.json',
        'projects/fixtures/projects.json',
        'employees/fixtures/user_data.json'
    ]

    def setUp(self):
        self.employeegrade = EmployeeGrade.objects.create(
            employee=User.objects.get(pk=1),
            grade=8,
            g_start_date=datetime.datetime.utcnow().date()
        )
        self.rp = ReportingPeriod.objects.create(
            start_date='1999-12-31',
            end_date='2000-01-06'
        )
        self.timecard = Timecard.objects.create(
            reporting_period=self.rp,
            user=self.employeegrade.employee,
            submitted=True
        )
        self.new_grade = EmployeeGrade.objects.create(
            employee=User.objects.get(pk=1),
            grade=8,
            g_start_date='1999-12-30'
        )

    def test_timecard_gets_grade_when_saved(self):
        tco = TimecardObject.objects.create(
            timecard=self.timecard,
            project=Project.objects.get(pk=1),
            hours_spent=40,
        )
        self.assertEqual(tco.grade, self.new_grade)
    def test_backwards_tco_update_w_grade_save(self):
        tco = TimecardObject.objects.create(
            timecard=self.timecard,
            project=Project.objects.get(pk=1),
            hours_spent=40,
        )
        new_grade = EmployeeGrade.objects.create(
            employee=User.objects.get(pk=1),
            grade=13,
            g_start_date='1999-12-31'
        )
        tco = TimecardObject.objects.get(
            timecard=self.timecard
        ).grade
        self.assertEqual(tco.grade, new_grade.grade)

    def test_unique_with_g_start_date(self):
        """Check that multiple EmployeeGrade objects with the same g_start_date
        cannot be saved for the same employee."""
        with self.assertRaises(IntegrityError):
            another_employeegrade = EmployeeGrade.objects.create(
            employee=User.objects.get(pk=1),
            grade=9,
            g_start_date=datetime.datetime.utcnow().date()
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
            end_date=datetime.date(2016, 1, 1),
            unit=1,
            is_18f_employee=True
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
            datetime.date(2016, 1, 1)
        )
        self.assertEqual(userdata.unit, 1)

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
