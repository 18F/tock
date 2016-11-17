import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test.client import Client

from django_webtest import WebTest


from ..views import get_fy_first_day, get_dates
from ..utils import get_fy_first_day, get_dates, calculate_utilization
from hours.models import ReportingPeriod, Timecard, TimecardObject
from projects.models import Project, AccountingCode, Agency
from employees.models import UserData


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
            submitted=True
        )

        self.b_timecard_object = TimecardObject.objects.create(
            timecard=self.timecard,
            project=b_project,
            hours_spent=25,
            submitted=True
        )

    def test_utilization(self):
        response = self.app.get(
            url=reverse('utilization:GroupUtilizationView'),
            headers={'X_AUTH_USER': 'aaron.snow@gsa.gov'}
        )

        self.assertEqual(len(
            response.context['unit_choices']), len(UserData.UNIT_CHOICES)
        )
        self.assertContains(response, 'regular.user')
        self.assertContains(response, 'aaron.snow')
        self.assertTrue(response.context['through_date'])
        self.assertTrue(response.context['recent_start_date'])
        self.assertEqual(len(response.context['user_list']), 2)
        self.assertTrue(response.context['user_list'][0].__dict__['last'])
        self.assertTrue(response.context['user_list'][0].__dict__['fytd'])
        self.assertTrue(response.context['user_list'][0].__dict__['recent'])
        self.assertTrue(
            response.context['user_list'][0].__dict__['_user_data_cache']
        )
        self.assertEqual(
            response.context['user_list'][0].__dict__['_user_data_cache'].__dict__['unit'], 0)
        #print(response.content)
