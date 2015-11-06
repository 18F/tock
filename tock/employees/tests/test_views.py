from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from django_webtest import WebTest

import datetime
from employees.views import parse_date
from employees.models import UserData


class UserViewTests(WebTest):

    fixtures = ['tock/fixtures/dev_user.json']
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

    def test_UserListViewPermissionforAdmin(self):
        """ Ensure that UserListView works for admin """
        response = self.app.get(
            reverse('employees:UserListView'),
            headers={'X_FORWARDED_EMAIL': 'test.user@gsa.gov'}
        )
        self.assertEqual(response.status_code, 200)
        # Check that only user's own edit links exposed for user
        self.assertEqual(
            len(response.html.find_all('a', href='/employees/test.user')), 1)
        self.assertEqual(
            len(response.html.find_all('a', href='/employees/regular.user')), 1)

    def test_UserListViewPermissionforUser(self):
        """ Ensure that UserListView works for a regular user """
        response = self.app.get(
            reverse('employees:UserListView'),
            headers={'X_FORWARDED_EMAIL': 'regular.user@gsa.gov'}
        )
        self.assertEqual(response.status_code, 200)
        # Check that only user's own edit links exposed for user
        self.assertEqual(
            len(response.html.find_all('a', href='/employees/test.user')), 0)
        self.assertEqual(
            len(response.html.find_all('a', href='/employees/regular.user')), 1)

    def test_UserFormViewPermissionForAdmin(self):
        """ Ensure that admin has access to another user's UserFormView
        page """
        response = self.app.get(
            reverse('employees:UserFormView', args=["regular.user"]),
            headers={'X_FORWARDED_EMAIL': 'test.user@gsa.gov'},
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
            reverse('employees:UserFormView', args=["test.user"]),
            headers={'X_FORWARDED_EMAIL': 'regular.user@gsa.gov'},
            status=403)
        self.assertEqual(response.status_code, 403)

    def test_UserFormViewPermissionForSelf(self):
        """ Ensure that UserFormViews works for a user's own form """
        response = self.app.get(
            reverse('employees:UserFormView', args=['regular.user']),
            headers={'X_FORWARDED_EMAIL': 'regular.user@gsa.gov'}
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
            headers={'X_FORWARDED_EMAIL': 'test.user@gsa.gov'},
        ).form
        form['first_name'] = 'Regular'
        form['last_name'] = 'User'
        form['start_date'] = '2013-01-01'
        form['end_date'] = '2014-01-01'
        response = form.submit(
            headers={'X_FORWARDED_EMAIL': 'test.user@gsa.gov'}).follow()
        # Check if errors occured at submission
        self.assertEqual(response.status_code, 200)
        # Check if data was changed
        # Check that data was changed
        user_data = UserData.objects.first()
        self.assertEqual(user_data.start_date, datetime.date(2013, 1, 1))
        self.assertEqual(user_data.end_date, datetime.date(2014, 1, 1))

    def test_UserFormViewPostForSelf(self):
        """ Check that a user can change thier own data via the form """
        form = self.app.get(
            reverse('employees:UserFormView', args=['regular.user']),
            headers={'X_FORWARDED_EMAIL': 'regular.user@gsa.gov'},
        ).form
        form['first_name'] = 'Regular'
        form['last_name'] = 'User'
        form['start_date'] = '2015-01-01'
        form['end_date'] = '2017-01-01'
        response = form.submit(
            headers={'X_FORWARDED_EMAIL': 'regular.user@gsa.gov'}).follow()
        # Check if errors occured at submission
        self.assertEqual(response.status_code, 200)
        # Check if data was changed
        # Check that data was changed
        user_data = UserData.objects.first()
        self.assertEqual(user_data.start_date, datetime.date(2015, 1, 1))
        self.assertEqual(user_data.end_date, datetime.date(2017, 1, 1))

    def test_UserFormViewPostForUser(self):
        """ Check that a user cannot change another users data """
        response = self.app.post_json(
            reverse('employees:UserFormView', args=['test.user']),
            params={
                'email': 'regular.user@gsa.gov',
                'first_name': 'Regular',
                'last_name': 'User',
                'start_date': '2015-01-01',
                'end_date': '2017-01-01'
            },
            headers={'X_FORWARDED_EMAIL': 'regular.user@gsa.gov'},
            status=403
        )
        # Check if errors occured at submission
        self.assertEqual(response.status_code, 403)
