import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model
from employees.models import EmployeeGrade, UserData
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

class EmployeeGradeTests(TestCase):
    fixtures = ['tock/fixtures/prod_user.json']

    def setUp(self):
        self.employeegrade = EmployeeGrade.objects.create(
            employee=User.objects.get(pk=1),
            grade=8,
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

    def setUp(self):
        self.regular_user = get_user_model().objects.create(
            username='aaron.snow')
        userdata = UserData(user=self.regular_user)
        userdata.start_date = datetime.date(2014, 1, 1)
        userdata.end_date = datetime.date(2016, 1, 1)
        userdata.unit = 1
        userdata.is_18f_employee = True
        userdata.save()
        self.token = Token.objects.create(user=self.regular_user)

    def test_string_method(self):
        """Check that string method override works correctly."""
        userdata = UserData.objects.get(user=self.regular_user)
        expected_string = str(userdata.user.username)
        self.assertEqual(expected_string, str(userdata))

    def test_user_data_is_stored(self):
        """ Check that user data was stored correctly """
        userdata = UserData.objects.first()
        self.assertEqual(
            userdata.start_date,
            datetime.date(2014, 1, 1))
        self.assertEqual(
            userdata.end_date,
            datetime.date(2016, 1, 1))
        self.assertEqual(userdata.unit, 1)

    def test_check_user_data_connected_to_user_model(self):
        """ Check that user data can be retrieved from User Model """
        self.assertEqual(
            self.regular_user.user_data.start_date,
            datetime.date(2014, 1, 1))
        self.assertEqual(
            self.regular_user.user_data.end_date,
            datetime.date(2016, 1, 1))
        self.assertEqual(
            self.regular_user.user_data.unit, 1)
        self.assertTrue(
            self.regular_user.user_data.is_18f_employee)

    def test_user_data_current_employee_default_is_true(self):
        """ Check that the user data is initalized with the current
        employee value being true """
        self.assertTrue(self.regular_user.user_data.current_employee)

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
