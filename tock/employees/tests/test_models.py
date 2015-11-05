import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model
from employees.models import UserData


class UserDataTests(TestCase):

    def setUp(self):
        self.regular_user = get_user_model().objects.create(
            username='test.user')
        userdata = UserData(user=self.regular_user)
        userdata.start_date = datetime.date(2014, 1, 1)
        userdata.end_date = datetime.date(2016, 1, 1)
        userdata.save()

    def test_user_data_is_stored(self):
        """ Check that user data was stored correctly """
        userdata = UserData.objects.first()
        self.assertEqual(
            userdata.start_date,
            datetime.date(2014, 1, 1))
        self.assertEqual(
            userdata.end_date,
            datetime.date(2016, 1, 1))

    def test_check_user_data_connected_to_user_model(self):
        """ Check that user data can be retrieved from User Model """
        self.assertEqual(
            self.regular_user.user_data.start_date,
            datetime.date(2014, 1, 1))
        self.assertEqual(
            self.regular_user.user_data.end_date,
            datetime.date(2016, 1, 1))
    
    def test_user_data_current_employee_default_is_true(self):
        """ Check that the user data is initalized with the current
        employee value being true """
        self.assertTrue(self.regular_user.user_data.current_employee)
