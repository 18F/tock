# -*- coding: utf-8 -*-

import datetime
import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from django_webtest import WebTest

from api.views import get_timecards, TimecardList
from employees.models import UserData, EmployeeGrade
from hours.factories import (
    UserFactory, ReportingPeriodFactory, TimecardFactory, TimecardObjectFactory,
)
from projects.factories import AccountingCodeFactory, ProjectFactory

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

User = get_user_model()

# common client for all API tests
def client():
    request_user = User.objects.get_or_create(username='aaron.snow')[0]
    token = Token.objects.get_or_create(user=request_user)[0].key
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client

# common fixtures for all API tests
FIXTURES = [
    'tock/fixtures/prod_user.json',
    'projects/fixtures/projects.json',
    'hours/fixtures/timecards.json'
]

class ProjectsAPITests(TestCase):
    fixtures = FIXTURES

    def test_projects_json(self):
        pass

class ProjectInstanceAPITests(WebTest):
    fixtures = FIXTURES

    def test_projects_json(self):
        res = client().get(reverse('ProjectInstanceView', kwargs={'pk': '29'})).data

        print('data len is %s' % len(data))
        self.assertTrue(res.has_key('name'))
        self.assertTrue(res.has_key('start_date'))
        self.assertTrue(res.has_key('end_date'))
        self.assertEqual(res['name'], "Consulting - Agile BPA")
        self.assertEqual(res['start_date'], "2016-01-01")
        self.assertEqual(res['end_date'], None)

class UsersAPITests(TestCase):
    fixtures = FIXTURES

    def test_users_json(self):
        pass

    def test_users_csv(self):
        pass

class TimecardsAPITests(WebTest):
    fixtures = FIXTURES

    def test_timecards_json(self):
        """ Check that the timecards are rendered in json format correctly """
        res = client().get(reverse('TimecardList'))
        print(res)
        #clean_res = json.loads(res.decode())
        #self.assertEqual(len(clean_res), 2)

    def test_timecards_grade_is_null_when_absent(self):
        #res = client().get(
        #    reverse('TimecardList'),
        #    data={'date': '2016-06-01'}).data
        #clean_res = json.loads(res.decode())
        #self.assertEqual(clean_res[0]['grade'], None)
        pass

    def test_timecards_grade_is_populated_when_present(self):
        res = client().get(
            reverse('TimecardList'),
            data={'date': '2015-06-01'}).data
        self.assertEqual(res['grade'], 4)

    # TODO: test with more diverse data
    def test_get_timecards(self):
        """ Check that get time cards returns the correct queryset """
        # Check with no params
        queryset = get_timecards(TimecardList.queryset)
        self.assertEqual(len(queryset), 2)
        # Check with after param
        queryset = get_timecards(TimecardList.queryset,
            params={'after': '2020-12-31'})
        self.assertEqual(len(queryset), 0)

        # Check with date param
        queryset = get_timecards(TimecardList.queryset,
                                 params={'date': '2000-01-01'})
        self.assertEqual(len(queryset), 0)
        queryset = get_timecards(TimecardList.queryset,
                                 params={'date': '2015-06-08'})
        self.assertEqual(len(queryset), 1)
        # Check with user param
        queryset = get_timecards(TimecardList.queryset,
                                 params={'user': '1'})
        self.assertEqual(len(queryset), 2)
        queryset = get_timecards(TimecardList.queryset,
                                 params={'user': 'aaron.snow'})
        self.assertEqual(len(queryset), 2)
        queryset = get_timecards(TimecardList.queryset,
                                 params={'user': '22'})
        self.assertEqual(len(queryset), 0)
        # Check with project param
        queryset = get_timecards(TimecardList.queryset,
                                 params={'project': '1'})
        self.assertEqual(len(queryset), 2)
        queryset = get_timecards(TimecardList.queryset,
                                 params={'project': 'Out Of Office'})
        self.assertEqual(len(queryset), 2)
        queryset = get_timecards(TimecardList.queryset,
                                 params={'project': '22'})
        self.assertEqual(len(queryset), 0)

    def test_get_unsubmitted_timecards(self):
        """ Check that get time cards returns the correct queryset """
        queryset = get_timecards(
            TimecardList.queryset,
            params={'submitted': 'no'}
        )
        self.assertEqual(len(queryset), 1)

        queryset = get_timecards(
            TimecardList.queryset,
            params={'submitted': 'yes'}
        )
        self.assertEqual(len(queryset), 2)

        queryset = get_timecards(
            TimecardList.queryset,
            params={'submitted': 'foo'}
        )
        self.assertEqual(len(queryset), 2)


class TestAggregates(WebTest):

    def setUp(self):
        super(TestAggregates, self).setUp()
        self.user = UserFactory()
        self.userdata = UserData.objects.create(user=self.user)
        self.billable_code = AccountingCodeFactory(billable=True)
        self.nonbillable_code = AccountingCodeFactory(billable=False)
        self.billable_project = ProjectFactory(accounting_code=self.billable_code)
        self.nonbillable_project = ProjectFactory(accounting_code=self.nonbillable_code)
        self.period = ReportingPeriodFactory(start_date=datetime.datetime(2015, 11, 1))
        self.timecard = TimecardFactory(user=self.user, reporting_period=self.period)
        self.grade = EmployeeGrade.objects.create(employee=self.user, grade=15, g_start_date=datetime.datetime(2016, 1, 1))
        self.timecard_objects = [
            TimecardObjectFactory(
                timecard=self.timecard,
                project=self.billable_project,
                hours_spent=15,
                grade=self.grade,
            ),
            TimecardObjectFactory(
                timecard=self.timecard,
                project=self.nonbillable_project,
                hours_spent=5,
                grade=self.grade
            ),
        ]

    def test_hours_by_quarter(self):
        response = client().get(reverse('HoursByQuarter')).data
        self.assertEqual(len(response), 1)
        row = response[0]
        self.assertEqual(row['billable'], 15)
        self.assertEqual(row['nonbillable'], 5)
        self.assertEqual(row['total'], 20)
        self.assertEqual(row['year'], 2016)
        self.assertEqual(row['quarter'], 1)

    def test_hours_by_quarter_with_unsubmitted_timecards(self):
        """ Check that unsubmitted timecards are not counted  """
        timecard_unsubmit = TimecardFactory(
            user=self.user,
            reporting_period=ReportingPeriodFactory(
                start_date=datetime.datetime(2015, 11, 2)
            ),
            submitted=False
        )
        self.timecard_objects.append([
            TimecardObjectFactory(
                timecard=timecard_unsubmit,
                project=self.billable_project,
                hours_spent=10,
            ),
        ])

        response = client().get(reverse('HoursByQuarter')).data
        self.assertEqual(len(self.timecard_objects), 3)
        self.assertEqual(response[0]['total'], 20)

    def test_hours_by_quarter_by_user(self):
        response = client().get(reverse('HoursByQuarterByUser')).data
        self.assertEqual(len(response), 1)
        row = response[0]
        self.assertEqual(row['username'], str(self.user))
        self.assertEqual(row['billable'], 15)
        self.assertEqual(row['nonbillable'], 5)
        self.assertEqual(row['total'], 20)
        self.assertEqual(row['year'], 2016)
        self.assertEqual(row['quarter'], 1)

    def test_hours_by_quarter_by_user_with_unsubmitted_timecards(self):
        """ Check that unsubmitted timecards are not counted  """
        # add one unsubmitted timecard + one additional submitted one
        timecard_unsubmit = TimecardFactory(
            user=self.user,
            reporting_period=ReportingPeriodFactory(
                start_date=datetime.datetime(2015, 11, 2)
            ),
            submitted=False
        )
        self.timecard_objects.append([
            TimecardObjectFactory(
                timecard=timecard_unsubmit,
                project=self.billable_project,
                hours_spent=10,
            ),
        ])

        timecard_submit = TimecardFactory(
            user=self.user,
            reporting_period=ReportingPeriodFactory(
                start_date=datetime.datetime(2015, 11, 3)
            ),
            submitted=True
        )
        self.timecard_objects.append([
            TimecardObjectFactory(
                timecard=timecard_submit,
                project=self.billable_project,
                hours_spent=40,
            ),
        ])

        response = client().get(reverse('HoursByQuarterByUser')).data
        row = response[0]

        self.assertEqual(len(self.timecard_objects), 4)
        self.assertEqual(row['total'], 60)

class ReportingPeriodList(WebTest):
    fixtures = FIXTURES

    def test_ReportingPeriodList_json(self):
        """ Check that the reporting periods are listed """
        res = client().get(reverse('ReportingPeriodList')).json()
        self.assertGreater(len(res), 0)

    def test_ReportingPeriodList_json_empty(self):
        """ Check that the ReportingPeriodList is empty when all users
        have filled out thier time cards"""
        reporting_periods = client().get(reverse('ReportingPeriodList')).data
        start_date = reporting_periods[0]['start_date']
        res = client().get(reverse(
                'ReportingPeriodAudit',
                kwargs={'reporting_period_start_date': start_date}
            )
        ).data
        self.assertEqual(len(res), 0)

    def test_ReportingPeriodList_json_missing_timesheet(self):
        """ Check that the ReportingPeriodList shows users that have missing
        time cards """
        # Create a user
        self.regular_user = User.objects.create(username='new.user')
        userdata = UserData(user=self.regular_user)
        userdata.save()

        reporting_periods = client().get(reverse('ReportingPeriodList')).data
        start_date = reporting_periods[0]['start_date']
        res = client().get(reverse(
                'ReportingPeriodAudit',
                kwargs={'reporting_period_start_date': start_date}
            )
        ).data
        self.assertEqual(len(res), 1)

    def test_ReportingPeriodList_json_no_longer_employed(self):
        """ Check that the ReportingPeriodList shows users that have missing
        time cards """
        # Create a user, but set the user as unemployed
        self.regular_user = User.objects.create(
            username='new.user')
        userdata = UserData(user=self.regular_user)
        userdata.current_employee = False
        userdata.save()

        reporting_periods = client().get(reverse('ReportingPeriodList')).data
        start_date = reporting_periods[0]['start_date']
        res = client().get(reverse(
                'ReportingPeriodAudit',
                kwargs={'reporting_period_start_date': start_date}
            )
        ).data
        self.assertEqual(len(res), 0)
