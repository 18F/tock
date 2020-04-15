import datetime

from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token
from organizations.models import Organization, Unit
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
            is_active=True
        )
        # Create Organization.
        self.regular_user_org = Organization.objects.create(
            name='18F',
            description='18F',
            active=True
        )
        # Create Unit.
        self.regular_user_unit = Unit.objects.create(
            name='Engineering',
            description='18F Engineering Chapter',
            org=self.regular_user_org,
            active=True
        )
        # Create UserData object related to regular_user.
        self.regular_user_userdata = UserData.objects.create(
            user=self.regular_user,
            start_date= datetime.date(2014, 1, 1),
            end_date=datetime.date(2100, 1, 1),
            is_18f_employee=True,
            current_employee=True,
            organization=self.regular_user_org,
            unit=self.regular_user_unit
        )
        # Create a sample reporting period
        self.reporting_period = ReportingPeriod.objects.create(
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2015, 1, 7),
            exact_working_hours=40,
            min_working_hours=40,
            max_working_hours=60,
            message='This is not a vacation'
        )
        # Create API token for regular_user.
        self.token = Token.objects.create(user=self.regular_user)

    def test_string_method(self):
        """Check that string method override works correctly."""
        userdata = self.regular_user_userdata
        expected_string = str(userdata.user.username)
        self.assertEqual(expected_string, str(userdata))

    def test_user_data_is_stored(self):
        """ Check that user data was stored correctly """
        userdata = self.regular_user_userdata
        self.assertEqual(
            userdata.start_date,
            datetime.date(2014, 1, 1)
        )
        self.assertEqual(
            userdata.end_date,
            datetime.date(2100, 1, 1)
        )
        self.assertEqual(userdata.unit, self.regular_user_unit)

    def test_is_late(self):
        """ Check if the user is late when no Timecard is present """
        userdata = self.regular_user_userdata
        self.assertEqual(userdata.is_late, True)
        # Now set  to false and re-check:
        userdata.billable_expectation = 0
        userdata.save()
        self.assertEqual(userdata.is_late, False)

    def test_organization_name(self):
        """
        Check to see if we can get organization name and unit correctly.
        And that the organization_name shortcut matches
        the name from the relationship.
        """
        userdata = self.regular_user_userdata
        self.assertEqual(userdata.organization.name, '18F')
        self.assertEqual(userdata.organization_name, '18F')
        self.assertEqual(userdata.unit.name, 'Engineering')

    def test_organization_name_empty(self):
        """ Check to see if we can get empty organization name"""
        # Create regular_user.
        user1 = User.objects.create(
            username='john.doe',
            is_superuser=True,
            is_staff=True,
            is_active=True
        )
        # Create UserData object related to regular_user.
        userdata1 = UserData.objects.create(
            user=user1,
            start_date= datetime.date(2014, 1, 1),
            end_date=datetime.date(2100, 1, 1),
            unit=self.regular_user_unit,
            is_18f_employee=True,
            current_employee=True
        )
        self.assertEqual(userdata1.organization_name, '')

    def test_is_not_late(self):
        """ Check if the user is not late when Timecard is present """
        userdata = self.regular_user_userdata
        timecard = Timecard.objects.create(
            user=self.regular_user,
            reporting_period=self.reporting_period,
            submitted=True
        )
        project = Project.objects.get(name="Platform as a Service")
        TimecardObject.objects.create(
            timecard=timecard,
            project=project,
            hours_spent=40)
        self.assertEqual(userdata.is_late, False)

    def test_employee_active(self):
        """ Check that the save() method correctly aligns UserData and User
         attributes when current_employee is True."""
        user = self.regular_user
        user.is_active = False
        user.save()
        status_before_save = user.is_active
        self.regular_user_userdata.current_employee = True
        self.regular_user_userdata.save()
        # now re-get the user object so we can see if the status
        # changed when userdata changed.
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
