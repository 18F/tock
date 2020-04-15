import datetime

from django.urls import reverse

from django_webtest import WebTest

from employees.views import parse_date
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
