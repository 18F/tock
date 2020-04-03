import datetime

from django.urls import reverse

from django_webtest import WebTest

from employees.views import parse_date
from employees.models import UserData
from hours.models import ReportingPeriod

from test_common import ProtectedViewTestCase


class UserViewTests(ProtectedViewTestCase, WebTest):
    csrf_checks = False

    def setUp(self):
        ReportingPeriod.objects.create(
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2015, 1, 7),
            exact_working_hours=40,
            min_working_hours=40,
            max_working_hours=60)

    def test_access_to_employee_static_view(self):
        self.login(username='regular.user')
        response = self.client.get(
            reverse('employees:UserDetailView', args=["regular.user"])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'First Name:',
            status_code=200
        )
        self.assertNotContains(
            response,
            '<form action="" method="post">',
            status_code=200
        )

    def test_access_to_user_form_for_self(self):
        self.login(username="aaron.snow")
        response = self.client.get(
            reverse('employees:UserListView')
        )
        self.assertContains(
            response,
            '<a href="/employees/e/aaron.snow">aaron.snow</a>',
            status_code=200
        )
        self.assertNotContains(
            response,
            '<a href="/employees/aaron.snow">aaron.snow</a>',
            status_code=200
        )

    def test_parse_date(self):
        """ Test that the parse date function returns datetime obj when
        input is not NA """
        date = 'NA'
        self.assertEqual(parse_date(date=date), None)
        date = "01/01/2013"
        self.assertEqual(parse_date(date=date), datetime.datetime(2013, 1, 1))

    def test_UserFormViewPermissionForAdmin(self):
        """ Ensure that admin has access to another user's UserFormView
        page """
        self.create_user(username='regular.user')
        self.login(username="aaron.snow", is_superuser=True)
        response = self.client.get(
            reverse('employees:UserFormView', args=["regular.user"])
        )
        # Check that initial data for UserDate Populates
        self.assertContains(
            response,
            '<input class="datepicker" id="id_start_date" name="start_date" type="text" value="2014-01-01">',
            html=True
        )
        self.assertContains(
            response,
            '<input class="datepicker" id="id_end_date" name="end_date" type="text" value="2016-01-01">',
            html=True
        )

    def test_UserFormViewPermissionForUser(self):
        """ Ensure that UserFormView returns a 403 when a user tries to access
        another user's form"""
        self.login(username="another.user", is_superuser=False)
        response = self.client.get(
            reverse('employees:UserFormView', args=["aaron.snow"])
        )
        self.assertEqual(response.status_code, 403)

    def test_UserFormViewPermissionForSelf(self):
        """ Ensure that UserFormViews works for a user's own form """
        self.login(username="test.user")
        response = self.client.get(
            reverse('employees:UserFormView', args=['test.user']),
        )
        self.assertEqual(response.status_code, 200)
        # Check that inital data for UserDate Populates
        self.assertContains(
            response,
            '<input class="datepicker" id="id_start_date" name="start_date" type="text" value="2014-01-01" />',
            html=True
        )
        self.assertContains(
            response,
            '<input class="datepicker" id="id_end_date" name="end_date" type="text" value="2016-01-01" />',
            html=True
        )

    def test_UserFormViewPostForAdmin(self):
        """ Ensure that an admin can submit data via the form """
        user = self.create_user(username='regular.user')
        self.login(username='aaron.snow', is_superuser=True)
        response = self.client.post(
            reverse('employees:UserFormView', args=['regular.user']),
            {
                'first_name': 'Regular',
                'last_name': 'User',
                'start_date': '2013-01-01',
                'end_date': '2014-01-01',
                'current_employee': False,
            }
        )
        # Check if errors occured at submission
        self.assertEqual(response.url, reverse('employees:UserListView'))
        # Check if data was changed
        # Check that data was changed
        user_data = UserData.objects.get(user=user)
        self.assertEqual(user_data.start_date, datetime.date(2013, 1, 1))
        self.assertEqual(user_data.end_date, datetime.date(2014, 1, 1))
        self.assertFalse(user_data.current_employee)

    def test_UserFormViewPostForSelf(self):
        """ Check that a user can change thier own data via the form """
        user = self.login(username="another.user")
        response = self.client.post(
            reverse('employees:UserFormView', args=['another.user']),
            {
                'first_name': 'Another',
                'last_name': 'User',
                'start_date': '2015-01-01',
                'end_date': '2017-01-01',
                'current_employee': False,
            }
        )
        # Check if errors occured at submission
        self.assertEqual(response.url, reverse('employees:UserListView'))
        # Check if data was changed
        # Check that data was changed
        user_data = UserData.objects.get(user=user)
        self.assertEqual(user_data.start_date, datetime.date(2015, 1, 1))
        self.assertEqual(user_data.end_date, datetime.date(2017, 1, 1))
        self.assertFalse(user_data.current_employee)

    def test_UserFormViewPostForUser(self):
        """ Check that a user cannot change another users data """
        response = self.client.post(
            reverse('employees:UserFormView', args=['aaron.snow']),
            {
                'email': 'regular.user@gsa.gov',
                'first_name': 'Regular',
                'last_name': 'User',
                'start_date': '2015-01-01',
                'end_date': '2017-01-01'
            },
            content_type='application/json'
        )
        # Check if errors occured at submission
        self.assertEqual(response.status_code, 403)
