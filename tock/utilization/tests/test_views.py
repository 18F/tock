import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from django_webtest import WebTest

from ..views import get_fy_first_day, get_dates
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
        periods = 4
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

        self.user = User.objects.create(
            username='regular.user'
        )
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
        print(self.user.is_staff)
        print(self.user)
        response = self.app.get(
            url=reverse('utilization:GroupUtilizationView'),
            headers={'X_AUTH_USER': 'aaron.snow@gsa.gov'}
        )

        self.assertEqual(len(
            response.context['unit_choices']), len(UserData.UNIT_CHOICES)
        )
