import datetime
from random import SystemRandom
from string import ascii_letters

from django.test import TestCase, SimpleTestCase

from employees.forms import UserForm, UserTravelRequestForm


class UserFormTests(TestCase):
    fixtures = ['tock/fixtures/prod_user.json']

    def test_user_update(self):
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'start_date': '2014-01-01',
            'end_date': '2016-01-01',
            'current_employee': False
        }
        form = UserForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['first_name'], "Test")
        self.assertEqual(form.cleaned_data['last_name'], "User")
        self.assertEqual(
            form.cleaned_data['start_date'], datetime.date(2014, 1, 1))
        self.assertEqual(
            form.cleaned_data['end_date'], datetime.date(2016, 1, 1))
        self.assertFalse(form.cleaned_data['current_employee'])

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


class UserTravelRequestFormTests(SimpleTestCase):
    today = datetime.date.today()
    one_day = datetime.timedelta(days=1)
    one_week = datetime.timedelta(weeks=1)

    def get_form_data(self):
        return {
            'requestor_name': 'Dan Siddoway',
            'requestor_email': 'dan@ds1.co',
            'billability': 'billable',
            'tock_project_name': 'Travel Request Form',
            'tock_project_id': '1337',
            'client_email': 'dan@blacksuncollective.net',
            'home_location': 'Thomas Hammer Coffee Roasters',
            'work_location': 'Spokane Public Library',
            'work_to_be_done': 'build an awesome travel request form',
            'departure_date': self.today,
            'return_date': self.today + self.one_week,
            'first_day_of_travel_work_date': self.today + self.one_day
        }

    def test_form_data_valid(self):
        form_data = self.get_form_data()

        form = UserTravelRequestForm(form_data)
        self.assertTrue(form.is_valid())

    def test_all_fields_required(self):
        form_data = self.get_form_data()

        for key, value in form_data.items():
            form_data[key] = ''

            form = UserTravelRequestForm(form_data)
            self.assertFalse(form.is_valid())

            form_data[key] = value

    def test_char_fields_max_length(self):
        form_data = self.get_form_data()

        char_fields = {
            'requestor_name',
            # 'billability',
            'tock_project_name',
            'tock_project_id',
            'home_location',
            'work_location',
            'work_to_be_done'
        }

        for char_field in char_fields.difference({'work_to_be_done'}):
            form_data[char_field] = ''.join([SystemRandom().choice(ascii_letters) for _ in range(255)])

        form_data['work_to_be_done'] = ''.join([SystemRandom().choice(ascii_letters) for _ in range(1023)])

        form = UserTravelRequestForm(form_data)
        self.assertTrue(form.is_valid())

        for char_field in char_fields.difference({'work_to_be_done'}):
            value = form_data[char_field]

            form_data[char_field] += ' '
            self.assertTrue(len(form_data[char_field]) > 255)

            form = UserTravelRequestForm(form_data)
            self.assertFalse(form.is_valid())

            form_data[char_field] = value
            self.assertTrue(len(form_data[char_field]) <= 255)

        value = form_data['work_to_be_done']

        form_data['work_to_be_done'] += ' '
        self.assertTrue(len(form_data['work_to_be_done']) > 1023)

        form = UserTravelRequestForm(form_data)
        self.assertFalse(form.is_valid())

        form_data['work_to_be_done'] = value
        self.assertTrue(len(form_data['work_to_be_done']) <= 1023)

    def test_email_fields_valid(self):
        form_data = self.get_form_data()

        for email_field in [
            'requestor_email',
            'client_email'
        ]:
            value = form_data[email_field]

            form_data[email_field] = ''.join([SystemRandom().choice(ascii_letters) for _ in range(256)])
            self.assertTrue(len(form_data[email_field]) > 255)

            form = UserTravelRequestForm(form_data)
            self.assertFalse(form.is_valid())

            form_data[email_field] = value
            self.assertTrue(len(form_data[email_field]) <= 255)

    def test_date_fields_valid(self):
        form_data = self.get_form_data()

        for date_field in [
            'departure_date',
            'first_day_of_travel_work_date',
            'return_date'
        ]:
            value = form_data[date_field]

            form_data[date_field] = self.today - SystemRandom().choice([self.one_day, self.one_week])
            self.assertTrue(form_data[date_field] < self.today)

            form = UserTravelRequestForm(form_data)
            self.assertFalse(form.is_valid())

            form_data[date_field] = value

    def test_date_fields_sequential(self):
        form_data = self.get_form_data()

        form_data['departure_date'] += self.one_week - self.one_day
        self.assertTrue(form_data['departure_date'] > form_data['first_day_of_travel_work_date'])

        form = UserTravelRequestForm(form_data)
        self.assertFalse(form.is_valid())

        form_data['departure_date'] = self.get_form_data()['departure_date']
        self.assertTrue(form_data['departure_date'] <= form_data['first_day_of_travel_work_date'])

        form_data['first_day_of_travel_work_date'] += self.one_week
        self.assertTrue(form_data['first_day_of_travel_work_date'] > form_data['return_date'])

        form = UserTravelRequestForm(form_data)
        self.assertFalse(form.is_valid())
