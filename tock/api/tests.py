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


# common fixtures for all API tests
FIXTURES = [
    'tock/fixtures/dev_user.json',
    'projects/fixtures/projects.json',
    'hours/fixtures/timecards.json'
]


class ProjectsAPITests(TestCase):
    fixtures = FIXTURES

    def test_projects_json(self):
        pass

    def test_projects_csv(self):
        pass


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
        self.assertEqual(res.json['count'], 1)

    def test_timecards_csv(self):
        """ Check that the timecards are rendered in csv format correctly """
        res = self.app.get(reverse('TimecardList', kwargs={'format': 'csv'}))
        self.assertEqual(len(res.text.strip().split('\n')), 2)

    # TODO: test with more diverse data
    def test_get_timecards(self):
        """ Check that get time cards returns the correct queryset """
        # Check with no params
        queryset = get_timecards(TimecardList.queryset)
        self.assertEqual(len(queryset), 1)
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
        self.assertEqual(len(queryset), 1)
        queryset = get_timecards(TimecardList.queryset,
                                 params={'user': 'test.user'})
        self.assertEqual(len(queryset), 1)
        queryset = get_timecards(TimecardList.queryset,
                                 params={'user': '22'})
        self.assertEqual(len(queryset), 0)
        # Check with project param
        queryset = get_timecards(TimecardList.queryset,
                                 params={'project': '1'})
        self.assertEqual(len(queryset), 1)
        queryset = get_timecards(TimecardList.queryset,
                                 params={'project': 'Out Of Office'})
        self.assertEqual(len(queryset), 1)
        queryset = get_timecards(TimecardList.queryset,
                                 params={'project': '22'})
        self.assertEqual(len(queryset), 0)


class ProjectTimelineTests(WebTest):
    fixtures = FIXTURES

    def test_project_timeline(self):
        res = self.app.get(reverse('UserTimelineView'))
        self.assertIn(
            'test.user,2015-06-01,2015-06-08,False,20.00', str(res.content))


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
            'modified_date',
            'hours_spent',
            'agency',
            'flat_rate',
        ))
        rows_read = 0
        for row in rows:
            self.assertEqual(set(row.keys()), expected_fields)
            self.assertEqual(row['project_id'], '1')
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
