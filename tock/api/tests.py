# -*- coding: utf-8 -*-

import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from django_webtest import WebTest

from api.views import get_timecardobjects, get_user_timecard_count, TimecardList
from employees.models import EmployeeGrade, UserData
from hours.models import Timecard
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
        self.assertTrue('name' in res)
        self.assertTrue('start_date' in res)
        self.assertTrue('end_date' in res)
        self.assertEqual(res['name'], "Consulting - Agile BPA")
        self.assertEqual(res['start_date'], "2016-01-01")
        self.assertEqual(res['end_date'], None)

class SubmissionsAPITests(WebTest):
    fixtures = FIXTURES

    def test_submissions_json_counts_punctual_timecard(self):
        res = client().get(reverse('Submissions', kwargs={'num_past_reporting_periods': 2})).data
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["on_time_submissions"], "1")

    def test_submissions_json_no_late_timecards(self):
        res = client().get(reverse('Submissions', kwargs={'num_past_reporting_periods': 1})).data
        self.assertEqual(len(res), 0)

    def test_submissions_json_too_many_periods(self):
        res = client().get(reverse('Submissions', kwargs={'num_past_reporting_periods': 100})).data
        self.assertEqual(len(res), 1)

    def test_user_timecard_count(self):
        """ Check with unfiltered query """
        all_timecards = get_user_timecard_count(Timecard.objects.all())
        self.assertEqual(all_timecards.first().tcount, 3)

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
        res = client().get(reverse('TimecardList')).data
        self.assertEqual(len(res), 2)

    def test_timecards_grade_is_null_when_absent(self):
        res = client().get(
            reverse('TimecardList'),
            kwargs={'date': '2016-06-01'}).data
        self.assertEqual(res[1]['grade'], None)

    def test_timecards_grade_is_populated_when_present(self):
        res = client().get(
            reverse('TimecardList'),
            kwargs={'date': '2015-06-01'}).data
        self.assertEqual(res[0]['grade'], 4)

    # TODO: test with more diverse data
    def test_get_timecardobjects(self):
        """ Check that get time cards returns the correct queryset """
        # Check with no params
        queryset = get_timecardobjects(TimecardList.queryset)
        self.assertEqual(len(queryset), 2)
        # Check with after param
        queryset = get_timecardobjects(TimecardList.queryset,
            params={'after': '2020-12-31'})
        self.assertEqual(len(queryset), 0)

        # Check with date param
        queryset = get_timecardobjects(TimecardList.queryset,
                                 params={'date': '2000-01-01'})
        self.assertEqual(len(queryset), 0)
        queryset = get_timecardobjects(TimecardList.queryset,
                                 params={'date': '2015-06-08'})
        self.assertEqual(len(queryset), 1)
        # Check with user param
        queryset = get_timecardobjects(TimecardList.queryset,
                                 params={'user': '1'})
        self.assertEqual(len(queryset), 2)
        queryset = get_timecardobjects(TimecardList.queryset,
                                 params={'user': 'aaron.snow'})
        self.assertEqual(len(queryset), 2)
        queryset = get_timecardobjects(TimecardList.queryset,
                                 params={'user': '22'})
        self.assertEqual(len(queryset), 0)
        # Check with project param
        queryset = get_timecardobjects(TimecardList.queryset,
                                 params={'project': '1'})
        self.assertEqual(len(queryset), 2)
        queryset = get_timecardobjects(TimecardList.queryset,
                                 params={'project': 'Out Of Office'})
        self.assertEqual(len(queryset), 2)
        queryset = get_timecardobjects(TimecardList.queryset,
                                 params={'project': '22'})
        self.assertEqual(len(queryset), 0)

        # Check with before param
        queryset = get_timecardobjects(TimecardList.queryset,
                                 params={'before': '2015-06-01'})
        self.assertEqual(len(queryset), 1)
        queryset = get_timecardobjects(TimecardList.queryset,
                                 params={'before': '2015-05-31'})
        self.assertEqual(len(queryset), 0)

        # Check with a range using before and after param
        queryset = get_timecardobjects(TimecardList.queryset,
                                 params={'after': '2015-06-01', 'before': '2016-05-31'})
        self.assertEqual(len(queryset), 1)
        queryset = get_timecardobjects(TimecardList.queryset,
                                 params={'after': '2015-06-01', 'before': '2016-06-01'})
        self.assertEqual(len(queryset), 1)


    def test_get_unsubmitted_timecards(self):
        """ Check that get time cards returns the correct queryset """
        queryset = get_timecardobjects(
            TimecardList.queryset,
            params={'submitted': 'no'}
        )
        self.assertEqual(len(queryset), 1)

        queryset = get_timecardobjects(
            TimecardList.queryset,
            params={'submitted': 'yes'}
        )
        self.assertEqual(len(queryset), 2)

        queryset = get_timecardobjects(
            TimecardList.queryset,
            params={'submitted': 'foo'}
        )
        self.assertEqual(len(queryset), 2)

"""
    Adding data to the timecards.json fixture results in failing tests since many tests
    assert on the length of a list returned. You can add tests here by creating mock data
    inside of setUp() and not worry about breaking existing tests that rely on the timecard
    fixture
"""
class FixturelessTimecardsAPITests(WebTest):
    def setUp(self):
        super(FixturelessTimecardsAPITests, self).setUp()
        self.user = UserFactory()
        self.userdata = UserData.objects.create(user=self.user)
        self.billable_code = AccountingCodeFactory(billable=True)
        self.weekly_billed_project = ProjectFactory(accounting_code=self.billable_code,is_weekly_bill=True)
        self.period1 = ReportingPeriodFactory(start_date=datetime.datetime(2021, 9, 1))
        self.period2 = ReportingPeriodFactory(start_date=datetime.datetime(2021, 9, 8))
        self.period3 = ReportingPeriodFactory(start_date=datetime.datetime(2021, 9, 14))
        self.period4 = ReportingPeriodFactory(start_date=datetime.datetime(2021, 9, 21))
        self.period5 = ReportingPeriodFactory(start_date=datetime.datetime(2021, 9, 29))
        self.full_allocation_timecard = TimecardFactory(user=self.user, reporting_period=self.period1)
        self.three_quarter_allocation_timecard = TimecardFactory(user=self.user, reporting_period=self.period2)
        self.half_allocation_timecard = TimecardFactory(user=self.user, reporting_period=self.period3)
        self.one_quarter_allocation_timecard = TimecardFactory(user=self.user, reporting_period=self.period4)
        self.one_eighth_allocation_timecard = TimecardFactory(user=self.user, reporting_period=self.period5)
        self.full_allocation_timecard_objects = [
            TimecardObjectFactory(
                timecard=self.full_allocation_timecard,
                project=self.weekly_billed_project,
                hours_spent=0,
                project_allocation=1.000
            )
        ]
        self.three_quarter_allocation_timecard_objects = [
            TimecardObjectFactory(
                timecard=self.three_quarter_allocation_timecard,
                project=self.weekly_billed_project,
                hours_spent=0,
               project_allocation=0.750
            )
        ]
        self.half_allocation_timecard_objects = [
            TimecardObjectFactory(
                timecard=self.half_allocation_timecard,
                project=self.weekly_billed_project,
                hours_spent=0,
                project_allocation=0.500
            )
        ]
        self.one_quarter_allocation_timecard_objects = [
            TimecardObjectFactory(
                timecard=self.one_quarter_allocation_timecard,
                project=self.weekly_billed_project,
                hours_spent=0,
                project_allocation=0.250
            )
        ]
        self.one_eighth_allocation_timecard_objects = [
            TimecardObjectFactory(
                timecard=self.one_eighth_allocation_timecard,
                project=self.weekly_billed_project,
                hours_spent=0,
                project_allocation=0.125
            )
        ]

    def test_project_allocation_scale_precision(self):
        """
            project_allocation allows a scale of 6 digits and a precision of 3 digits
            Test to make sure that the API, which relies on TimecardSerializer, follows this convention
        """
        all_timecards = client().get(
            reverse('TimecardList'),
            kwargs={'date': '2021-09-01'}).data

        full_allocation_timecard = all_timecards[0]
        three_quarter_allocation_timecard = all_timecards[1]
        half_allocation_timecard = all_timecards[2]
        one_quarter_allocation_timecard = all_timecards[3]
        one_eighth_allocation_timecard = all_timecards[4]

        self.assertEqual(full_allocation_timecard['project_allocation'], "1.000")
        self.assertEqual(three_quarter_allocation_timecard['project_allocation'], "0.750")
        self.assertEqual(half_allocation_timecard['project_allocation'], "0.500")
        self.assertEqual(one_quarter_allocation_timecard['project_allocation'], "0.250")
        self.assertEqual(one_eighth_allocation_timecard['project_allocation'], "0.125")

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

class FullTimecardsAPITests(WebTest):
    fixtures = FIXTURES

    def test_with_no_filters_only_returns_submitted_timecards(self):
        res = client().get(reverse('FullTimecardList')).data
        self.assertEqual(len(res), 2)
        self.assertTrue(all(tc['submitted'] for tc in res))

    def test_unsubmitted_filter(self):
        res = client().get(
            reverse('FullTimecardList'), {'submitted': 'no'}
        ).data
        self.assertEqual(len(res), 1)
        self.assertFalse(all(tc['submitted'] for tc in res))

    def test_date_filter(self):
        date_to_filter_on = '2015-06-04'
        res = client().get(
            reverse('FullTimecardList'), {'date': date_to_filter_on}
        ).data
        self.assertEqual(len(res), 1)
        self.assertTrue(res[0]['reporting_period_start_date'] < date_to_filter_on)
        self.assertTrue(res[0]['reporting_period_end_date'] > date_to_filter_on)

    def test_after_filter(self):
        # Note that the default behavior is to only return completed timecards, so even though
        # there may be another later timecard (in our fixtures), it may or may not be
        # submitted (and if not, won't show up in the response)
        date_to_filter_on = '2016-01-01'
        res = client().get(
            reverse('FullTimecardList'), {'after': date_to_filter_on}
        ).data
        self.assertEqual(len(res), 1)
        self.assertTrue(res[0]['reporting_period_start_date'] > date_to_filter_on)
        self.assertTrue(res[0]['reporting_period_end_date'] > date_to_filter_on)

    def test_before_filter(self):
        date_to_filter_on = '2016-01-01'
        res = client().get(
            reverse('FullTimecardList'), {'after': date_to_filter_on}
        ).data
        self.assertEqual(len(res), 1)
        self.assertTrue(res[0]['reporting_period_start_date'] > date_to_filter_on)
        self.assertTrue(res[0]['reporting_period_end_date'] > date_to_filter_on)

    def test_bad_date_format_returns_400(self):
        res = client().get(
            reverse('FullTimecardList'),
            {'date': 'N0T-A-D8'}
        )
        self.assertEqual(res.status_code, 400)