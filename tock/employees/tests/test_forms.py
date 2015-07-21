import datetime

from django.test import TestCase
from employees.forms import UserForm


class UserFormTests(TestCase):
    fixtures = ['tock/fixtures/dev_user.json']

    def test_user_update(self):
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'start_date': '2014-01-01',
            'end_date': '2016-01-01'
        }
        form = UserForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['first_name'], "Test")
        self.assertEqual(form.cleaned_data['last_name'], "User")
        self.assertEqual(
            form.cleaned_data['start_date'], datetime.date(2014, 1, 1))
        self.assertEqual(
            form.cleaned_data['end_date'], datetime.date(2016, 1, 1))

    def test_date_validation(self):
        form_data = {'email': 'testuser@gsa.gov', 'end_date': '2015-01-01'}
        form = UserForm(form_data)
        self.assertFalse(form.is_valid())
        form_data = {
            'email': 'testuser@gsa.gov',
            'start_date': '2015-02-01',
            'end_date': '2015-01-01'}
        form = UserForm(form_data)
        self.assertFalse(form.is_valid())
        form_data = {
            'email': 'testuser@gsa.gov',
            'start_date': '2015-01-01',
            'end_date': '2015-05-05'}
        form = UserForm(form_data)
        self.assertTrue(form.is_valid())
