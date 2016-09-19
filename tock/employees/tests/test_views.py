import datetime
import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django_webtest import WebTest

from employees.models import UserData
from employees.views import parse_date


class UserViewTests(WebTest):

    fixtures = ['tock/fixtures/prod_user.json']
    csrf_checks = False

    def setUp(self):
        self.regular_user = get_user_model().objects.create(
            username="regular.user")
        self.regular_user.save()
        UserData(
            user=self.regular_user,
            start_date=datetime.datetime(2014, 1, 1),
            end_date=datetime.datetime(2016, 1, 1)
        ).save()

    def test_parse_date(self):
        """ Test that the parse date function returns datetime obj when
        input is not NA """
        date = 'NA'
        self.assertEqual(parse_date(date=date), None)
        date = "01/01/2013"
        self.assertEqual(parse_date(date=date), datetime.datetime(2013, 1, 1))

#    def test_UserListViewPermissionforAdmin(self):
#        """ Ensure that UserListView works for admin """
#        response = self.app.get(
#            reverse('employees:UserListView'),
#            headers={'X_AUTH_USER': 'aaron.snow@gsa.gov'}
#        )
#        self.assertEqual(response.status_code, 200)
#        # Check that only user's own edit links exposed for user
#        self.assertEqual(
#            len(response.html.find_all('a', href='/employees/aaron.snow')), 1)
#        self.assertEqual(
#            len(response.html.find_all('a', href='/employees/regular.user')), 1)
#
#    def test_UserListViewPermissionforUser(self):
#        """ Ensure that UserListView works for a regular user """
#        response = self.app.get(
#            reverse('employees:UserListView'),
#            headers={'X_AUTH_USER': 'regular.user@gsa.gov'}
#        )
#        self.assertEqual(response.status_code, 200)
#        # Check that only user's own edit links exposed for user
#        self.assertEqual(
#            len(response.html.find_all('a', href='/employees/aaron.snow')), 1)
#        self.assertEqual(
#            len(response.html.find_all('a', href='/employees/regular.user')), 1)

    def test_UserFormViewPermissionForAdmin(self):
        """ Ensure that admin has access to another user's UserFormView
        page """
        response = self.app.get(
            reverse('employees:UserFormView', args=["regular.user"]),
            headers={'X_AUTH_USER': 'aaron.snow@gsa.gov'},
        )
        # Check that inital data for UserDate Populates
        self.assertEqual(
            response.html.find('input', {'id': 'id_start_date'})['value'],
            '2014-01-01')
        self.assertEqual(
            response.html.find('input', {'id': 'id_end_date'})['value'],
            '2016-01-01')

    def test_UserFormViewPermissionForUser(self):
        """ Ensure that UserFormView returns a 403 when a user tries to access
        another user's form"""
        response = self.app.get(
            reverse('employees:UserFormView', args=["aaron.snow"]),
            headers={'X_AUTH_USER': 'regular.user@gsa.gov'},
            status=403)
        self.assertEqual(response.status_code, 403)

    def test_UserFormViewPermissionForSelf(self):
        """ Ensure that UserFormViews works for a user's own form """
        response = self.app.get(
            reverse('employees:UserFormView', args=['regular.user']),
            headers={'X_AUTH_USER': 'regular.user@gsa.gov'}
        )
        self.assertEqual(response.status_code, 200)
        # Check that inital data for UserDate Populates
        self.assertEqual(
            response.html.find('input', {'id': 'id_start_date'})['value'],
            '2014-01-01')
        self.assertEqual(
            response.html.find('input', {'id': 'id_end_date'})['value'],
            '2016-01-01')

    def test_UserFormViewPostForAdmin(self):
        """ Ensure that an admin can submit data via the form """
        form = self.app.get(
            reverse('employees:UserFormView', args=['regular.user']),
            headers={'X_AUTH_USER': 'aaron.snow@gsa.gov'},
        ).form
        form['first_name'] = 'Regular'
        form['last_name'] = 'User'
        form['start_date'] = '2013-01-01'
        form['end_date'] = '2014-01-01'
        form['current_employee'] = False
        response = form.submit(
            headers={'X_AUTH_USER': 'aaron.snow@gsa.gov'}).follow()
        # Check if errors occured at submission
        self.assertEqual(response.status_code, 200)
        # Check if data was changed
        # Check that data was changed
        user_data = UserData.objects.first()
        self.assertEqual(user_data.start_date, datetime.date(2013, 1, 1))
        self.assertEqual(user_data.end_date, datetime.date(2014, 1, 1))
        self.assertFalse(user_data.current_employee)

    def test_UserFormViewPostForSelf(self):
        """ Check that a user can change thier own data via the form """
        form = self.app.get(
            reverse('employees:UserFormView', args=['regular.user']),
            headers={'X_AUTH_USER': 'regular.user@gsa.gov'},
        ).form
        form['first_name'] = 'Regular'
        form['last_name'] = 'User'
        form['start_date'] = '2015-01-01'
        form['end_date'] = '2017-01-01'
        form['current_employee'] = False
        response = form.submit(
            headers={'X_AUTH_USER': 'regular.user@gsa.gov'}).follow()
        # Check if errors occured at submission
        self.assertEqual(response.status_code, 200)
        # Check if data was changed
        # Check that data was changed
        user_data = UserData.objects.first()
        self.assertEqual(user_data.start_date, datetime.date(2015, 1, 1))
        self.assertEqual(user_data.end_date, datetime.date(2017, 1, 1))
        self.assertFalse(user_data.current_employee)

    def test_UserFormViewPostForUser(self):
        """ Check that a user cannot change another users data """
        response = self.app.post_json(
            reverse('employees:UserFormView', args=['aaron.snow']),
            params={
                'email': 'regular.user@gsa.gov',
                'first_name': 'Regular',
                'last_name': 'User',
                'start_date': '2015-01-01',
                'end_date': '2017-01-01'
            },
            headers={'X_AUTH_USER': 'regular.user@gsa.gov'},
            status=403
        )
        # Check if errors occured at submission
        self.assertEqual(response.status_code, 403)


class UserTravelRequestFormViewTest(WebTest):
    def test_send_travel_form_email(self):
        today = datetime.date.today()
        one_day = datetime.timedelta(days=1)
        one_week = datetime.timedelta(weeks=1)

        form_data = {
            'requestor_name': 'Aaron Snow',
            'requestor_email': 'aaron.snow@gsa.gov',
            'billability': 'billable',
            'tock_project_name': 'Travel Request Form',
            'tock_project_id': '1337',
            'client_email': 'dan@blacksuncollective.net',
            'home_location': 'Thomas Hammer Coffee Roasters',
            'work_location': 'Spokane Public Library',
            'work_to_be_done': 'build an awesome travel request form',
            'departure_date': today,
            'return_date': today + one_week,
            'first_day_of_travel_work_date': today + one_day
        }

        header_fields = [
            'billability',
            'tock_project_name',
            'tock_project_id',
            'departure_date',
            'return_date'
        ]
        body_fields = [
            'home_location',
            'work_location',
            'departure_date',
            'return_date',
            'work_to_be_done',
            'first_day_of_travel_work_date',
            'requestor_name'
        ]

        form = self.app.get(
            reverse(
                'employees:UserTravelRequestFormView',
                kwargs={'username': 'aaron.snow'}
            ),
            headers={'X_FORWARDED_EMAIL': 'aaron.snow@gsa.gov'}
        ).form

        for key, value in form_data.items():
            form[key] = value

        form.submit(
            headers={'X_FORWARDED_EMAIL': 'aaron.snow@gsa.gov'}
        ).follow()

        self.assertEqual(len(mail.outbox), 1)

        for field in header_fields:
            if re.search(r'_date$', field):
                pass
            else:
                self.assertTrue(re.search(str(form_data[field]), mail.outbox[0].subject))

        for field in body_fields:
            if re.search(r'_date$', field):
                pass
            else:
                self.assertTrue(re.search(str(form_data[field]), mail.outbox[0].body))
