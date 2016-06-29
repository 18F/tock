# -*- coding: utf-8 -*-

import csv
import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse

from django_webtest import WebTest

from api.views import get_timecards, TimecardList
from projects.factories import AccountingCodeFactory, ProjectFactory
from hours.factories import (
    UserFactory, ReportingPeriodFactory, TimecardFactory, TimecardObjectFactory,
)

from django.contrib.auth import get_user_model
from employees.models import UserData


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

    def test_projects_csv(self):
        pass


class ProjectInstanceAPITests(WebTest):
    fixtures = FIXTURES

    def test_projects_json(self):
        res = self.app.get(reverse('ProjectInstanceView', kwargs={'pk': '29'}))
        self.assertEqual(res.json['name'], "Consulting - Agile BPA")
        self.assertEqual(res.json['start_date'], "2016-01-01")
        self.assertEqual(res.json['end_date'], None)

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
        res = self.app.get(reverse('TimecardList', kwargs={'format': 'json'}))
        self.assertEqual(res.json['count'], 2)

    def test_timecards_csv(self):
        """ Check that the timecards are rendered in csv format correctly """
        res = self.app.get(reverse('TimecardList', kwargs={'format': 'csv'}))
        self.assertEqual(len(res.text.strip().split('\n')), 3)

    # TODO: test with more diverse data
    def test_get_timecards(self):
        """ Check that get time cards returns the correct queryset """
        # Check with no params
        queryset = get_timecards(TimecardList.queryset)
        self.assertEqual(len(queryset), 2)
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


class ProjectTimelineTests(WebTest):
    fixtures = FIXTURES

    def test_project_timeline(self):
        res = self.app.get(reverse('UserTimelineView'))
        self.assertIn(
            'aaron.snow,2015-06-01,2015-06-08,False,20.00', str(res.content))


class BulkTimecardsTests(TestCase):
    fixtures = FIXTURES

    def test_bulk_timecards(self):
        response = self.client.get(reverse('BulkTimecardList'))
        rows = decode_streaming_csv(response)
        expected_fields = set((
            'project_name',
            'project_id',
            'billable',
            'employee',
            'start_date',
            'end_date',
            'hours_spent',
            'agency',
            'flat_rate',
            'active',
            'mbnumber',
            'notes',
        ))
        rows_read = 0
        for row in rows:
            self.assertEqual(set(row.keys()), expected_fields)
            self.assertEqual(row['project_id'], '1')
            rows_read += 1
        self.assertNotEqual(rows_read, 0, 'no rows read, expecting 1 or more')

class BulkTimecardsTests(TestCase):
    fixtures = FIXTURES

    def test_slim_bulk_timecards(self):
        response = self.client.get(reverse('SlimBulkTimecardList'))
        rows = decode_streaming_csv(response)
        expected_fields = set((
            'project_name',
            'billable',
            'employee',
            'start_date',
            'end_date',
            'hours_spent',
            'mbnumber',
        ))
        rows_read = 0
        for row in rows:
            self.assertEqual(set(row.keys()), expected_fields)
            self.assertEqual(row['project_name'], 'Out Of Office')
            self.assertEqual(row['billable'], 'False')
            rows_read += 1
        self.assertNotEqual(rows_read, 0, 'no rows read, expecting 1 or more')


def decode_streaming_csv(response, **reader_options):
    lines = [line.decode('utf-8') for line in response.streaming_content]
    return csv.DictReader(lines, **reader_options)


class TestAggregates(WebTest):

    def setUp(self):
        super(TestAggregates, self).setUp()
        self.user = UserFactory()
        self.billable_code = AccountingCodeFactory(billable=True)
        self.nonbillable_code = AccountingCodeFactory(billable=False)
        self.billable_project = ProjectFactory(accounting_code=self.billable_code)
        self.nonbillable_project = ProjectFactory(accounting_code=self.nonbillable_code)
        self.period = ReportingPeriodFactory(start_date=datetime.datetime(2015, 11, 1))
        self.timecard = TimecardFactory(user=self.user, reporting_period=self.period)
        self.timecard_objects = [
            TimecardObjectFactory(
                timecard=self.timecard,
                project=self.billable_project,
                hours_spent=15,
            ),
            TimecardObjectFactory(
                timecard=self.timecard,
                project=self.nonbillable_project,
                hours_spent=5,
            ),
        ]

    def test_hours_by_quarter(self):
        response = self.app.get(reverse('HoursByQuarter'))
        self.assertEqual(len(response.json), 1)
        row = response.json[0]
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

        response = self.app.get(reverse('HoursByQuarter'))
        self.assertEqual(len(self.timecard_objects), 3)
        self.assertEqual(response.json[0]['total'], 20)

    def test_hours_by_quarter_by_user(self):
        response = self.app.get(reverse('HoursByQuarterByUser'))
        self.assertEqual(len(response.json), 1)
        row = response.json[0]
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

        response = self.app.get(reverse('HoursByQuarterByUser'))
        row = response.json[0]

        self.assertEqual(len(self.timecard_objects), 4)
        self.assertEqual(row['total'], 60)


class ReportingPeriodList(WebTest):
    fixtures = FIXTURES

    def test_ReportingPeriodList_json(self):
        """ Check that the reporting periods are listed """
        res = self.app.get(reverse('ReportingPeriodList'))
        self.assertEqual(res.json['count'], 1)

    def test_ReportingPeriodList_json(self):
        """ Check that the ReportingPeriodList is empty when all users
        have filled out thier time cards"""
        reporting_periods = self.app.get(reverse('ReportingPeriodList'))
        start_date = reporting_periods.json['results'][0]['start_date']
        res = self.app.get(reverse(
                'ReportingPeriodAudit',
                kwargs={'reporting_period_start_date': start_date}
            )
        )
        self.assertEqual(res.json['count'], 0)

    def test_ReportingPeriodList_json_missing_timesheet(self):
        """ Check that the ReportingPeriodList shows users that have missing
        time cards """
        # Create a user
        self.regular_user = get_user_model().objects.create(
            username='new.user')
        userdata = UserData(user=self.regular_user)
        userdata.save()

        reporting_periods = self.app.get(reverse('ReportingPeriodList'))
        start_date = reporting_periods.json['results'][0]['start_date']
        res = self.app.get(reverse(
                'ReportingPeriodAudit',
                kwargs={'reporting_period_start_date': start_date}
            )
        )
        self.assertEqual(res.json['count'], 1)


    def test_ReportingPeriodList_json_no_longer_employed(self):
        """ Check that the ReportingPeriodList shows users that have missing
        time cards """
        # Create a user, but set the user as unemployed
        self.regular_user = get_user_model().objects.create(
            username='new.user')
        userdata = UserData(user=self.regular_user)
        userdata.current_employee = False
        userdata.save()

        reporting_periods = self.app.get(reverse('ReportingPeriodList'))
        start_date = reporting_periods.json['results'][0]['start_date']
        res = self.app.get(reverse(
                'ReportingPeriodAudit',
                kwargs={'reporting_period_start_date': start_date}
            )
        )
        self.assertEqual(res.json['count'], 0)
