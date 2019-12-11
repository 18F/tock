import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from django_webtest import WebTest

from ..utils import get_fy_first_day, get_dates
from hours.models import ReportingPeriod, Timecard, TimecardObject
from projects.models import Project, AccountingCode, Agency
from employees.models import UserData

User = get_user_model()

FIXTURES = [
    'tock/fixtures/prod_user.json',
    'projects/fixtures/projects.json',
    'hours/fixtures/timecards.json',
    'employees/fixtures/user_data.json',
]


class TestUtils(TestCase):
    fixtures = FIXTURES

    def test_fy_first_date(self):
        date = datetime.date(2014, 7, 4)
        self.assertEqual(get_fy_first_day(date), datetime.date(2013, 10, 1))

    def test_get_dates(self):
        periods = ReportingPeriod.objects.count() -1
        result = get_dates(periods)
        self.assertEqual(len(result), 5)
        self.assertTrue(result[1] <= result[2])
        self.assertFalse(result[2] == result[3])

class TestGroupUtilizationView(WebTest):
    fixtures = [
        'projects/fixtures/projects.json',
    ]

    def setUp(self):
        nb_acct = AccountingCode.objects.create(
            code='foo',
            billable=False,
            agency=Agency.objects.first()
        )

        b_acct = nb_acct
        b_acct.billable = True
        b_acct.save()

        nb_project = Project.objects.first()
        nb_project.accounting_code = nb_acct
        nb_project.save()

        b_project = Project.objects.last()
        b_project.accounting_code = b_acct
        b_project.save()

        req_user = User.objects.get_or_create(username='aaron.snow')[0]
        req_user.is_staff = True
        req_user.save()

        req_user_data = UserData.objects.get_or_create(user=req_user)[0]
        req_user_data.unit = 0
        req_user_data.is_billable = True
        req_user_data.save()

        self.req_user = req_user

        self.user = User.objects.create(
            username='regular.user'
        )
        self.user_data = UserData.objects.get_or_create(user=self.user)[0]
        self.user_data.unit = 0
        self.user_data.save()

        self.reporting_period = ReportingPeriod.objects.create(
            start_date=datetime.date(2015, 10, 1),
            end_date=datetime.date(2015, 10, 7)
        )
        self.timecard = Timecard.objects.create(
            reporting_period=self.reporting_period,
            user=self.user,
            submitted=True
        )

        self.nb_timecard_object = TimecardObject.objects.create(
            timecard=self.timecard,
            project=nb_project,
            hours_spent=15,
        )

        self.b_timecard_object = TimecardObject.objects.create(
            timecard=self.timecard,
            project=b_project,
            hours_spent=25,
        )

    def test_utilization(self):
        response = self.app.get(
            url=reverse('utilization:GroupUtilizationView'),
            user=self.req_user
        )
        self.assertEqual(len(
            response.context['object_list']), len(UserData.UNIT_CHOICES)
        )
        self.assertContains(response, 'regular.user')
        self.assertContains(response, 'aaron.snow')
        self.assertTrue(response.context['through_date'])
        self.assertTrue(response.context['recent_start_date'])
        self.assertEqual(len(response.context['object_list'][0]['billable_staff']), 2)
        self.assertTrue(response.context['object_list'][0]['last'])
        self.assertTrue(response.context['object_list'][0]['fytd'])
        self.assertTrue(response.context['object_list'][0]['recent'])
        self.assertEqual(
            response.context['object_list'][0]['billable_staff'][0].unit, 0
        )

    def test_summary_rows(self):
        response = self.app.get(
            url=reverse('utilization:GroupUtilizationView'),
            user=self.req_user
        )
        self.assertEqual(
            response.context['object_list'][0]['recent']['total_hours'],
            (self.b_timecard_object.hours_spent + \
            self.nb_timecard_object.hours_spent)
        )
        # Update hours spent.
        self.b_timecard_object.hours_spent = 33.33
        self.b_timecard_object.save()
        response = self.app.get(
            url=reverse('utilization:GroupUtilizationView'),
            user=self.req_user
        )
        self.assertContains(response,int(
            self.b_timecard_object.hours_spent + \
            self.nb_timecard_object.hours_spent)
        )
