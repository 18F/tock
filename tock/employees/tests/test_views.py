from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

import datetime
from employees.views import parse_date, UserListView
from employees.models import UserData


class UserViewTests(TestCase):

    fixtures = ['tock/fixtures/dev_user.json']

    def setUp(self):
        self.regular_user = get_user_model().objects.create(
            username="regular.user")
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

    def test_UserListViewPermissionforAdmin(self):
        """ Ensure that UserListView works for admin """
        c = Client(HTTP_X_FORWARDED_EMAIL='test.user@gsa.gov')
        response = c.get(
            reverse('employees:UserListView'),
            follow=True)
        self.assertEqual(response.status_code, 200)
        # Check that all users' edit links exposed for admin
        self.assertContains(
            response, '<a href="/employees/test.user">test.user</a>')
        self.assertContains(
            response, '<a href="/employees/regular.user">regular.user</a>')

    def test_UserListViewPermissionforUser(self):
        """ Ensure that UserListView works for a regular user """
        c = Client(HTTP_X_FORWARDED_EMAIL='regular.user@gsa.gov')
        response = c.get(
            reverse('employees:UserListView'),
            follow=True)
        self.assertEqual(response.status_code, 200)
        # Check that only user's own edit links exposed for user
        self.assertNotContains(
            response, '<a href="/employees/test.user">test.user</a>')
        self.assertContains(
            response, '<a href="/employees/regular.user">regular.user</a>')

    def test_UserFormViewPermissionForAdmin(self):
        """ Ensure that admin has access to another user's UserFormView
        page """
        c = Client(HTTP_X_FORWARDED_EMAIL='test.user@gsa.gov')
        response = c.get(
            reverse('employees:UserFormView', args=["regular.user"]),
            follow=True)
        self.assertEqual(response.status_code, 200)
        # Check that inital data for UserDate Populates
        self.assertContains(response, 'value="2016-01-01"')
        self.assertContains(response, 'value="2014-01-01"')

    def test_UserFormViewPermissionForUser(self):
        """ Ensure that UserFormView returns a 403 when a user tries to access
        another user's form"""
        c = Client(HTTP_X_FORWARDED_EMAIL='regular.user@gsa.gov')
        response = c.get(
            reverse('employees:UserFormView', args=["test.user"]), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_UserFormViewPermissionForSelf(self):
        """ Ensure that UserFormViews works for a user's own form """
        c = Client(HTTP_X_FORWARDED_EMAIL='regular.user@gsa.gov')
        response = c.get(
            reverse('employees:UserFormView', args=["regular.user"]),
            follow=True)
        self.assertEqual(response.status_code, 200)
        # Check that inital data for UserDate Populates
        self.assertContains(response, 'value="2016-01-01"')
        self.assertContains(response, 'value="2014-01-01"')

    def test_UserFormViewPostForAdmin(self):
        """ Ensure that an admin can change user data via the form """
        c = Client(HTTP_X_FORWARDED_EMAIL='test.user@gsa.gov')
        response = c.post(
            reverse('employees:UserFormView', args=['regular.user']),
            data={
                'email': 'regular.user@gsa.gov',
                'first_name': 'Regular',
                'last_name': 'User',
                'start_date': '2015-01-01',
                'end_date': '2017-01-01'
            },
            follow=True)
        # Check if errors occured at submission
        self.assertEqual(response.status_code, 200)
        # Check if submission form redirects to list view
        self.assertTrue(
            isinstance(response.context_data['view'], UserListView))
        # Check that data was changed
        self.assertEqual(
            response.context_data['object_list'][1].user_data.start_date,
            datetime.date(2015, 1, 1))
        self.assertEqual(
            response.context_data['object_list'][1].user_data.end_date,
            datetime.date(2017, 1, 1))

    def test_UserFormViewPostForSelf(self):
        """ Check that a user can change thier own data via the form """
        c = Client(HTTP_X_FORWARDED_EMAIL='regular.user@gsa.gov')
        response = c.post(
            reverse('employees:UserFormView', args=['regular.user']),
            data={
                'email': 'regular.user@gsa.gov',
                'first_name': 'Regular',
                'last_name': 'User',
                'start_date': '2015-01-01',
                'end_date': '2017-01-01'
            },
            follow=True)
        # Check if errors occured at submission
        self.assertEqual(response.status_code, 200)
        # Check if submission form redirects to list view
        self.assertTrue(
            isinstance(response.context_data['view'], UserListView))
        # Check that data was changed
        self.assertEqual(
            response.context_data['object_list'][1].user_data.start_date,
            datetime.date(2015, 1, 1))
        self.assertEqual(
            response.context_data['object_list'][1].user_data.end_date,
            datetime.date(2017, 1, 1))

    def test_UserFormViewPostForUser(self):
        """ Check that a user cannot change another users data """
        c = Client(HTTP_X_FORWARDED_EMAIL='regular.user@gsa.gov')
        response = c.post(
            reverse('employees:UserFormView', args=['test.user']),
            data={
                'email': 'regular.user@gsa.gov',
                'first_name': 'Regular',
                'last_name': 'User',
                'start_date': '2015-01-01',
                'end_date': '2017-01-01'
            },
            follow=True)
        # Check if errors occured at submission
        self.assertEqual(response.status_code, 403)
