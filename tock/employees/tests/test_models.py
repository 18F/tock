import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model
from employees.models import UserData
from django.contrib.auth.models import User


class UserDataTests(TestCase):

    def setUp(self):
        self.regular_user = User.objects.create(
            username='aaron.snow',
            is_superuser=True,
            is_staff=True,
            is_active=True)
        self.userdata = UserData(user=self.regular_user)
        self.userdata.start_date = datetime.date(2014, 1, 1)
        self.userdata.end_date = datetime.date(2016, 1, 1)
        self.userdata.unit = 1
        self.userdata.is_18f_employee = True
        self.userdata.save()

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

    def test_employee_not_active(self):
        """ Check that the save() method correctly aligns UserData and User
         attributes when current_employee is False."""
        user_before_save = User.objects.get(
            username=self.regular_user.username)
        user_active = user_before_save.is_active
        user_superuser = user_before_save.is_superuser
        user_staff = user_before_save.is_staff
        self.userdata.current_employee = False
        self.userdata.save()

        user_after_save = User.objects.get(
            username=self.regular_user.username)

        self.assertNotEqual(user_active, user_after_save.is_active)
        self.assertNotEqual(user_staff, user_after_save.is_staff)
        self.assertNotEqual(user_superuser, user_after_save.is_superuser)

    def test_employee_active(self):
        """ Check that the save() method correctly aligns UserData and User
         attributes when current_employee is True."""
        user = User.objects.get(
            username=self.regular_user.username)
        user.is_active = False
        user.save()
        status_before_save = User.objects.get(
            username=self.regular_user.username).is_active
        self.userdata.current_employee = True
        self.userdata.save()

        status_after_save = User.objects.get(
            username=self.regular_user.username).is_active

        self.assertNotEqual(status_before_save, status_after_save)
