import datetime
import csv
import requests

from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django_webtest import WebTest

from api.renderers import stream_csv

from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from api.tests import client
from api.views import UserDataSerializer, ProjectSerializer
from employees.models import UserData
from hours.utils import number_of_hours
from hours.forms import choice_label_for_project
from tock.settings import base, dev
from hours.views import GeneralSnippetsTimecardSerializer
import hours.models
import hours.views
import projects.models

FIXTURES = [
    'tock/fixtures/prod_user.json',
    'projects/fixtures/projects.json',
    'hours/fixtures/timecards.json',
    'employees/fixtures/user_data.json',
]

def decode_streaming_csv(response, **reader_options):
    lines = [line.decode('utf-8') for line in response.streaming_content]
    return csv.DictReader(lines, **reader_options)

class DashboardReportsListTests(WebTest):
    fixtures = ['tock/fixtures/prod_user.json',]

    def setUp(self):
        self.user = User.objects.first()
        self.rp_1 = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2016, 10, 1),
            end_date=datetime.date(2016, 10, 7)
        )
        self.rp_2 = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2016, 10, 8),
            end_date=datetime.date(2016, 10, 14)
        )

    def test_response_ok(self):
        response = self.app.get(
            reverse('reports:DashboardReportsList'),
            headers={'X_AUTH_USER': self.user.email},
        )
        self.assertEqual(response.status_code, 200)

    def test_template_render(self):
        response = self.app.get(
            reverse('reports:DashboardReportsList'),
            headers={'X_AUTH_USER': self.user.email},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            hours.models.ReportingPeriod.objects.all().count(),
            len(response.context['reportingperiod_list'])
        )

class DashboardViewTests(WebTest):
    fixtures = [
        'tock/fixtures/prod_user.json',
        'projects/fixtures/projects.json',
        'employees/fixtures/user_data.json'
    ]

    def setUp(self):
        self.user = User.objects.first()
        self.ud = UserData.objects.first()
        self.ud.user = self.user
        self.ud.unit = 0
        self.ud.save()
        self.rp_1 = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2016, 10, 1),
            end_date=datetime.date(2016, 10, 7),
            exact_working_hours=40
        )
        self.rp_2 = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2016, 10, 8),
            end_date=datetime.date(2016, 10, 14),
            exact_working_hours=40
        )
        self.target = hours.models.Targets.objects.create(
            start_date=datetime.date(2016, 10, 1),
            end_date=datetime.date(2017, 9, 30),
            revenue_target_cr=100,
            revenue_target_plan=80,
            hours_target_cr=80,
            hours_target_plan=40,
            labor_rate=100,
            periods=40
        )
        self.timecard_1 = hours.models.Timecard.objects.create(
            reporting_period=self.rp_1,
            user=self.user,
            submitted=True
        )
        self.timecard_2 = hours.models.Timecard.objects.create(
            reporting_period=self.rp_2,
            user=self.user,
            submitted=True
        )

        ac_1 = projects.models.AccountingCode.objects.first()
        ac_1.billable = True
        ac_1.save()
        ac_2 = projects.models.AccountingCode.objects.last()
        ac_2.billable = False
        ac_2.save()
        self.project_1 = projects.models.Project.objects.first()
        self.project_1.accounting_code = ac_1
        self.project_1.save()
        self.project_2 = projects.models.Project.objects.last()
        self.project_2.accounting_code = ac_2
        self.project_2.save()

        to_1 = hours.models.TimecardObject.objects.create(
            timecard=self.timecard_1,
            project=self.project_1,
            hours_spent=30,
            submitted=True
        )
        to_2 = hours.models.TimecardObject.objects.create(
            timecard=self.timecard_1,
            project=self.project_2,
            hours_spent=10,
            submitted=True
        )
        to_3 = hours.models.TimecardObject.objects.create(
            timecard=self.timecard_2,
            project=self.project_1,
            hours_spent=15,
            submitted=True
        )
        to_4 = hours.models.TimecardObject.objects.create(
            timecard=self.timecard_2,
            project=self.project_2,
            hours_spent=25,
            submitted=True
        )

    def test_response_ok(self):
        response = self.app.get(
            reverse(
                'reports:DashboardView',
                kwargs={'reporting_period':'1999-12-31'}
            ),
            headers={'X_AUTH_USER': self.user.email},
        )
        self.assertEqual(response.status_code, 200)

    def test_response_w_params_ok(self):
        response = self.app.get(
            reverse(
                'reports:DashboardView',
                kwargs={'reporting_period':'1999-12-31'}
            ),
            {'unit':'1'},
            headers={'X_AUTH_USER': self.user.email},
        )
        self.assertEqual(response.status_code, 200)

    def test_acq_exclusion(self):
        date = self.rp_2.end_date.strftime('%Y-%m-%d')
        response = self.app.get(
            reverse(
                'reports:DashboardView',
                kwargs={'reporting_period': date}
            ),
            headers={'X_AUTH_USER': self.user.email},
        )
        self.assertNotContains(response, '<td>$-2 (-100.00%)</td>')

        p_l = projects.models.ProfitLossAccount.objects.create(
            name='FY17 Acquisition Svcs Billable',
        )
        self.project_1.profit_loss_account = p_l
        self.project_1.save()
        self.project_2.profit_loss_account = p_l
        self.project_2.save()
        response = self.app.get(
            reverse(
                'reports:DashboardView',
                kwargs={'reporting_period': date}
            ),
            headers={'X_AUTH_USER': self.user.email},
        )
        self.assertContains(response, '<td>$-2 (-100.00%)</td>')

    def test_no_reporting_period(self):
        """Tests errors are handled when there is no matching reporting
        period."""
        response = self.app.get(
            reverse(
                'reports:DashboardView',
                kwargs={'reporting_period':'1999-12-31'}
            ),
            headers={'X_AUTH_USER': self.user.email},
        )
        self.assertContains(response, 'Whoops!')
        self.assertContains(response, '1999-12-31')

    def test_no_targets(self):
        """Tests that errors are handled when there is a reporting period but
        no targets for that reporting period."""
        for obj in hours.models.Targets.objects.all():
            obj.delete()
        date = hours.models.ReportingPeriod.objects.first().start_date.strftime(
            '%Y-%m-%d'
        )
        response = self.app.get(
            reverse(
                'reports:DashboardView',
                kwargs={'reporting_period': date}
            ),
            headers={'X_AUTH_USER': self.user.email},
        )
        self.assertContains(response, 'Whoops')
        self.assertContains(response, date)

        """def test_unit_param(self):
        date = self.rp_2.end_date.strftime('%Y-%m-%d')
        self.ud.unit = 13
        self.ud.save()
        response = self.app.get(
            reverse(
                'reports:DashboardView',
                kwargs={'reporting_period': date}
            ),
            {'unit':'13'},
            headers={'X_AUTH_USER': self.user.email},
        )
        self.assertEqual(
            response.context['units'],
            [(self.ud.unit, self.ud.get_unit_display())]
        )
        self.assertEqual(
            response.context['variance_rev_cr_weekly'],
            '$1,498'
        )
        response = self.app.get(
            reverse(
                'reports:DashboardView',
                kwargs={'reporting_period': date}
            ),
            {'unit':'1'},
            headers={'X_AUTH_USER': self.user.email},
        )
        self.assertEqual(
            response.context['variance_rev_cr_weekly'],
            '$0'
        )"""
    def test_template_render(self):
        date = self.rp_2.end_date.strftime('%Y-%m-%d')
        response = self.app.get(
            reverse(
                'reports:DashboardView',
                kwargs={'reporting_period': date}
            ),
            headers={'X_AUTH_USER': self.user.email},
        )
        self.assertContains(response, '<td>$4,500</td>')
        self.assertContains(response, '<td>13.0 (650.00%)</td>')
        self.assertContains(response, '<td>$1,498 (59900.00%)</td>')
        self.assertNotContains(response, '<td>$-2 (-100.00%)</td>')

        # Test that units are correctly excluded.
        self.ud.unit = 4
        self.ud.save()
        response = self.app.get(
            reverse(
                'reports:DashboardView',
                kwargs={'reporting_period': date}
            ),
            headers={'X_AUTH_USER': self.user.email},
        )
        self.assertContains(response, '<td>$-2 (-100.00%)</td>')
        self.assertNotContains(response, '<td>$1,498 (59900.00%)</td>')

        """self.ud.unit = 13
        self.ud.save()
        response = self.app.get(
            reverse(
                'reports:DashboardView',
                kwargs={'reporting_period': date}
            ),
            {'unit':'1'},
            headers={'X_AUTH_USER': self.user.email},
        )
        self.assertContains(
            response,
            '<td>$0 (0.00%)</td>',
            html=True
        )

        response = self.app.get(
            reverse(
                'reports:DashboardView',
                kwargs={'reporting_period': date}
            ),
            {'unit':'13'},
            headers={'X_AUTH_USER': self.user.email},
        )
        self.assertContains(
            response,
            '<td>14.0 (1400.00%)</td>',
            html=True
        )"""

    def test_random_but_viable_date(self):
        """Tests that a date that is not a start date or end date of a
        reporting period returns a valid and correct response."""
        date = '2016-10-03'
        response = self.app.get(
            reverse(
                'reports:DashboardView',
                kwargs={'reporting_period': date}
            ),
            headers={'X_AUTH_USER': self.user.email},
        )

        self.assertContains(response, '18F Operations Dashboard')
        self.assertEqual(response.context['rp_selected'], self.rp_1)

class CSVTests(TestCase):
    fixtures = FIXTURES

    def test_user_data_csv(self):
        """Test that correct fields are returned for user data CSV request."""
        response = client(self).get(reverse('reports:UserDataView'))
        rows = decode_streaming_csv(response)
        for row in rows:
            num_of_fields = len(row)
        num_of_expected_fields = len(
            UserDataSerializer.__dict__['_declared_fields']
        )

        self.assertEqual(num_of_expected_fields, num_of_fields)

    def test_project_csv(self):
        """Test that correct fields are returned for project data CSV
        request."""
        response = client(self).get(reverse('reports:ProjectList'))
        rows = decode_streaming_csv(response)
        for row in rows:
            num_of_fields = len(row)
        num_of_expected_fields = len(
            ProjectSerializer.__dict__['Meta'].__dict__['fields']
        )
        self.assertEqual(num_of_expected_fields, num_of_fields)

    def test_general_snippets(self):
        """Test that snippets are returned in correct CSV format."""
        project = projects.models.Project.objects.get_or_create(
            name='General'
        )[0]
        tco = hours.models.TimecardObject.objects.first()
        tco.project = project
        tco.hours_spent = 40
        tco.notes = 'Some notes about things!'
        tco.save()

        response = client(self).get(reverse('reports:GeneralSnippetsView'))
        rows = decode_streaming_csv(response)
        entry_found = False
        for row in rows:
                num_of_fields = len(row)
                if tco.notes in row['notes']:
                        entry_found = True
                        break
        expected_num_of_fields = \
            len(GeneralSnippetsTimecardSerializer.__dict__['_declared_fields'])
        self.assertEqual(num_of_fields, expected_num_of_fields)
        self.assertTrue(entry_found)

class BulkTimecardsTests(TestCase):
    fixtures = FIXTURES

    def test_bulk_timecards(self):
        response = client(self).get(reverse('reports:BulkTimecardList'))
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
            'revenue_profit_loss_account',
            'revenue_profit_loss_account_name',
            'expense_profit_loss_account',
            'expense_profit_loss_account_name'
        ))
        rows_read = 0
        for row in rows:
            self.assertEqual(set(row.keys()), expected_fields)
            self.assertEqual(row['project_id'], '1')
            rows_read += 1
        self.assertNotEqual(rows_read, 0, 'no rows read, expecting 1 or more')

    def test_slim_bulk_timecards(self):
        response = client(self).get(reverse('reports:SlimBulkTimecardList'))
        rows = decode_streaming_csv(response)
        expected_fields = set((
            'project_name',
            'project_id',
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

class TestAdminBulkTimecards(TestCase):
    fixtures = FIXTURES

    def test_admin_bulk_timecards(self):
        factory = RequestFactory()
        user = User.objects.get(username='aaron.snow')
        request = factory.get(reverse('reports:AdminBulkTimecardList'))
        request.user = user
        response = hours.views.admin_bulk_timecard_list(request)
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
            'grade',
            'revenue_profit_loss_account',
            'revenue_profit_loss_account_name',
            'expense_profit_loss_account',
            'expense_profit_loss_account_name'
        ))
        for row in rows:
            self.assertEqual(set(row.keys()), expected_fields)

class ProjectTimelineTests(WebTest):
    fixtures = FIXTURES

    def test_project_timeline(self):
        res = client(self).get(reverse('reports:UserTimelineView'))
        self.assertIn(
            'aaron.snow,2015-06-01,2015-06-08,False,20.00', str(res.content))

class UtilTests(TestCase):

    def test_number_of_hours_util(self):
        """Ensure the number of hours returns a correct value"""
        self.assertEqual(20, number_of_hours(50, 40))

class UserReportsTest(TestCase):
    fixtures = [
        'tock/fixtures/prod_user.json',
        'projects/fixtures/projects.json',
        'employees/fixtures/user_data.json'
    ]
    def setUp(self):
        self.user = User.objects.first()
        user_data = UserData.objects.first()
        user_data.user = self.user
        user_data.save()

        self.reporting_period = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(1999, 12, 31),
            end_date=datetime.date(2000, 1, 1)
        )
        self.timecard = hours.models.Timecard.objects.create(
            user=self.user,
            reporting_period=self.reporting_period
        )
        self.nonbillable_project = hours.models.Project.objects.filter(
            accounting_code__billable=False
        )[0]
        self.billable_project = projects.models.Project.objects.filter(
            accounting_code__billable=True
        )[0]
        self.timecard_obj_0 = hours.models.TimecardObject.objects.create(
            timecard=self.timecard,
            project=self.nonbillable_project,
            hours_spent=13
        )
        self.timecard_obj_1 = hours.models.TimecardObject.objects.create(
            timecard=self.timecard,
            project=self.billable_project,
            hours_spent=27
        )

    def test_user_reporting_period_report(self):
        response = client(self).get(reverse(
            'reports:ReportingPeriodUserDetailView',
            kwargs={'reporting_period':'1999-12-31', 'username':'aaron.snow'}
        ))
        self.assertEqual(response.context['user_utilization'], '67.5%')
        self.assertEqual(response.context['user_all_hours'], 40.00)
        self.assertEqual(response.context['user_billable_hours'], 27)
        self.assertContains(response, '67.5%')

class ReportTests(WebTest):
    fixtures = [
        'projects/fixtures/projects.json',
        'tock/fixtures/prod_user.json',
    ]
    csrf_checks = False

    def setUp(self):
        self.reporting_period = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2015, 1, 7),
            exact_working_hours=40)
        self.user = get_user_model().objects.get(id=1)
        self.userdata = UserData.objects.create(user=self.user)
        self.timecard = hours.models.Timecard.objects.create(
            user=self.user,
            submitted=True,
            reporting_period=self.reporting_period)
        self.project_1 = projects.models.Project.objects.get(name="openFEC")
        self.project_2 = projects.models.Project.objects.get(
            name="Peace Corps")
        self.timecard_object_1 = hours.models.TimecardObject.objects.create(
            timecard=self.timecard,
            project=self.project_1,
            hours_spent=12)
        self.timecard_object_2 = hours.models.TimecardObject.objects.create(
            timecard=self.timecard,
            project=self.project_2,
            hours_spent=28)
        self.regular_user = get_user_model().objects.create(
            username='john',
            email='john@gsa.gov',
            is_superuser=False,
        )
        self.regular_user.save()
        UserData(
            user=self.regular_user,
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2017, 1, 1),
        ).save()
        self.former_employee = get_user_model().objects.create(
            username='maya',
            email='maya@gsa.gov',
            is_superuser=False,
        )
        self.regular_user.save()
        UserData(
            user=self.former_employee,
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2017, 1, 1),
            current_employee=False,
        ).save()

    def test_ReportList_get_queryset(self):
        hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2016, 1, 1),
            end_date=datetime.date(2016, 1, 7),
            exact_working_hours=40)
        response = self.app.get(reverse('reports:ListReports'))
        response = response.content.decode('utf-8')
        self.assertTrue(response.index('2016') < response.index('2015'))

    def test_report_list_authenticated(self):
        """ Check that main page loads with reporting periods for authenticated
        user with with userdata """
        response = self.app.get(
            reverse('ListReportingPeriods'),
            headers={'X_AUTH_USER': self.regular_user.email},
        )
        self.assertEqual(response.status_code, 200)

    def test_auto_create_reporting_period(self):
        """ Check that a reporting period is automatically created if the
        previous reporting period has ended. """
        existing_rps = hours.models.ReportingPeriod.objects.all()
        response = self.app.get(
            reverse('ListReportingPeriods'),
            headers={'X_AUTH_USER': self.regular_user.email},
        )
        new_rps = hours.models.ReportingPeriod.objects.all()
        self.assertNotEqual(existing_rps, new_rps)
        self.assertEqual(
            new_rps.first().start_date,
            (self.reporting_period.end_date + datetime.timedelta(days=1))
        )
        self.assertEqual(
            new_rps.first().end_date,
            (self.reporting_period.end_date +  \
             datetime.timedelta(days=1)) + \
             datetime.timedelta(days=6)
        )

    def test_auto_create_reporting_period_fy_end(self):
        """ Check that a reporting period is NOT automatically created if
        the reporting period span two fiscal years. """
        self.reporting_period.end_date = datetime.date(
            year=2015, month=9, day=30)
        self.reporting_period.save()
        existing_rps = hours.models.ReportingPeriod.objects.all()
        response = self.app.get(
            reverse('ListReportingPeriods'),
            headers={'X_AUTH_USER': self.regular_user.email},
        )
        new_rps = hours.models.ReportingPeriod.objects.all()
        self.assertEqual(len(existing_rps), len(new_rps))

    def test_disallowed_dates_safe_dates(self):
        """ Check that dates are correctly disallowed when auto-creating a new
        reporting period."""
        safe_end_dates = [(2011, 9, 28), (2011, 10, 2), (2016, 9, 29),
            (2016, 10, 3)]
        ct_existing_rps = len(hours.models.ReportingPeriod.objects.all())
        for i in safe_end_dates:
            self.reporting_period.end_date = datetime.date(
                year=i[0], month=i[1], day=i[2])
            self.reporting_period.save()
            response = self.app.get(
                reverse('ListReportingPeriods'),
                headers={'X_AUTH_USER': self.regular_user.email},
            )
            ct_new_rps = len(hours.models.ReportingPeriod.objects.all())
            self.assertNotEqual(ct_existing_rps, ct_new_rps)

    def test_disallowed_dates_not_safe_dates(self):
        """ Check that dates are correctly allowed when auto-creating a new
        reporting period."""
        not_safe_end_dates = [(2015, 10, 2), (2015, 9, 30), (2014, 10, 2),
            (2014, 9, 30)]
        ct_existing_rps = len(hours.models.ReportingPeriod.objects.all())
        for i in not_safe_end_dates:
            self.reporting_period.end_date = datetime.date(
                year=i[0], month=i[1], day=i[2])
            self.reporting_period.save()
            response = self.app.get(
                reverse('ListReportingPeriods'),
                headers={'X_AUTH_USER': self.regular_user.email},
            )
            ct_new_rps = len(hours.models.ReportingPeriod.objects.all())
            self.assertEqual(ct_existing_rps, ct_new_rps)

    def test_disallowed_dates_irrelevant_dates(self):
        """ Check that dates are correctly disallowed / allowed when
        auto-creating a new reporting period. """
        irrelevant_end_dates = [(2015, 2, 2), (2015, 11, 30)]
        ct_existing_rps = len(hours.models.ReportingPeriod.objects.all())
        for i in irrelevant_end_dates:
            self.reporting_period.end_date = datetime.date(
                year=i[0], month=i[1], day=i[2])
            self.reporting_period.save()
            response = self.app.get(
                reverse('ListReportingPeriods'),
                headers={'X_AUTH_USER': self.regular_user.email},
            )
            ct_new_rps = len(hours.models.ReportingPeriod.objects.all())
            self.assertNotEqual(ct_existing_rps, ct_new_rps)

    def test_dont_auto_create_rp(self):
        """ Check that a new reporting period is NOT created if the current
        reporting period has not ended. """
        ct_existing_rps = len(hours.models.ReportingPeriod.objects.all())
        today = datetime.date.today()
        end_date = today + datetime.timedelta(days=1)
        self.reporting_period.start_date = today
        self.reporting_period.end_date = today + datetime.timedelta(days=1)
        self.reporting_period.save()
        response = self.app.get(
            reverse('ListReportingPeriods'),
            headers={'X_AUTH_USER': self.regular_user.email},
        )
        ct_new_rps = len(hours.models.ReportingPeriod.objects.all())
        self.assertEqual(ct_existing_rps, ct_new_rps)

    def test_dont_auto_create_rp_if_no_rps(self):
        """ Check that no attempt to auto-create a reporting period is made
        if no reporting periods exist. """
        self.reporting_period.delete()
        response = self.app.get(
            reverse('ListReportingPeriods'),
            headers={'X_AUTH_USER': self.regular_user.email},
        )
        self.assertIsNotNone(hours.models.ReportingPeriod.objects.all())


    def test_reportperiod_updatetimesheet_self(self):
        """
        Test that users can access their own timesheets update forms
        """
        date = self.reporting_period.start_date.strftime('%Y-%m-%d')
        response = self.app.get(
            reverse(
                'reportingperiod:UpdateTimesheet',
                kwargs={'reporting_period': date}
            ),
            headers={'X_AUTH_USER': self.regular_user.email},
        )
        self.assertEqual(response.status_code, 200)

    def test_float_data_is_correct(self):
        """Check that correct Float data is delivered to timecard_form
        template."""
        new_reporting_period = self.reporting_period
        new_reporting_period.start_date = datetime.date(2016, 5, 1)
        new_reporting_period.end_date = datetime.date(2016, 5, 8)
        new_reporting_period.save()
        date = self.reporting_period.start_date.strftime('%Y-%m-%d')
        response = self.app.get(
            reverse(
                'reportingperiod:UpdateTimesheet',
                kwargs={'reporting_period': date}
            ),
            headers={'X_AUTH_USER': '6cfl4j.c4drwz@gsa.gov'},
        )
        self.assertIn('7.5 hours on NYbNJGuffc', response)

    def test_holiday_prefill(self):
        """Tests when a holiday is related to a reporting period that it is
        contained in the timecard formset."""

        # Additional test set up.
        self.timecard_object_1.delete()
        self.timecard_object_2.delete()
        holiday_prefills = hours.models.HolidayPrefills.objects.create(
            project=self.project_1,
            hours_per_period=8
        )
        reporting_period_w_holiday = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2016, 1, 1),
            end_date=datetime.date(2016, 1, 7),
            exact_working_hours=40
        )
        reporting_period_w_holiday.holiday_prefills.add(holiday_prefills)
        reporting_period_w_holiday.save()
        self.timecard.reporting_period = reporting_period_w_holiday
        self.timecard.save()
        # Get response from TimecardView.
        response = self.app.get(
            reverse(
                'reportingperiod:UpdateTimesheet',
                kwargs={'reporting_period': '2016-01-01'}
            ),
            headers={'X_AUTH_USER': self.user.email},
        )

        # Checks response context for the prefilled project and hours.
        project_found = False
        str_formset = str(response.context['formset']).split('\n')
        for line in str_formset:
            if line.find('selected') > 0 and \
            line.find(
                'option value="{}"'.format(
                    holiday_prefills.project.id
                )
            ) > 0:
                project_found = True
        self.assertTrue(project_found)
        hours_found = False
        hours_spent_str = str(holiday_prefills.hours_per_period)
        for line in str_formset:
            if line.find('id_timecardobjects-0-hours_spent') > 0 and \
            line.find(hours_spent_str) > 0:
                hours_found = True
        self.assertTrue(hours_found)

        # Removes related holiday prefill and checks that prefilled project is
        # not found in a new respeonse.
        reporting_period_w_holiday.holiday_prefills.clear()
        response = self.app.get(
            reverse(
                'reportingperiod:UpdateTimesheet',
                kwargs={'reporting_period': '2016-01-01'}
            ),
            headers={'X_AUTH_USER': self.user.email},
        )
        str_formset = str(response.context['formset']).split('\n')
        for line in str_formset:
            if line.find('selected') > 0 and line.find('option value=""') > 0:
                project_found = False
        self.assertFalse(project_found)

    def test_prefilled_timecard(self):
        """
        Test that new timecard form is prefilled with
        last (submitted) timecard's projects
        """
        new_period = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2016, 1, 1),
            end_date=datetime.date(2016, 1, 7),
        )
        date = new_period.start_date.strftime('%Y-%m-%d')

        response = self.app.get(
            reverse(
                'reportingperiod:UpdateTimesheet',
                kwargs={'reporting_period': date}
            ),
            headers={'X_AUTH_USER': self.user.email},
        )

        # projects prefilled in the html
        prefilled_projects = response.html.find_all(
            'div', {'class': 'entry-project'}
        )[:-1]
        prefilled_projects_names = set(
            p.find('option', {'selected': True}).text
            for p in prefilled_projects
        )
        scrubbed_projects_names = []
        for n in prefilled_projects_names:
            n = n.split(' - ')[1] if ' - ' in n else n
            scrubbed_projects_names.append(n)
        prefilled_projects_names = set(scrubbed_projects_names)

        # projects based on last submitted timecard
        last_timecard_projects = set(
            choice_label_for_project(tco.project) for tco
            in self.timecard.timecardobjects.all()
        )
        scrubbed_projects_names = []
        for n in last_timecard_projects:
            n = n.split(' - ')[1] if ' - ' in n else n
            scrubbed_projects_names.append(n)
        last_timecard_projects = set(scrubbed_projects_names)


        self.assertEqual(prefilled_projects_names, last_timecard_projects)

        # ensure hours field is left blank
        prefilled_hours = set(
            e.find('input').get('value') for e in
            response.html.find_all('div', {'class': 'entry-amount'})[:-1]
        )
        self.assertEqual(prefilled_hours, {None})

    def test_do_not_prefill_timecard(self):
        """
        Test that a timecard doesn't get prefilled
        if it already has its own entries
        """
        new_period = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2016, 1, 1),
            end_date=datetime.date(2016, 1, 7),
        )
        new_timecard = hours.models.Timecard.objects.create(
            user=self.user,
            submitted=False,
            reporting_period=new_period
        )
        new_project = projects.models.Project.objects.get(name="Midas")
        new_tco = hours.models.TimecardObject.objects.create(
            timecard=new_timecard,
            project=new_project,
            hours_spent=10.12
        )

        date = new_period.start_date.strftime('%Y-%m-%d')
        response = self.app.get(
            reverse(
                'reportingperiod:UpdateTimesheet',
                kwargs={'reporting_period': date}
            ),
            headers={'X_AUTH_USER': self.user.email},
        )
        first_hour_val = response.html \
            .find('div', {'class': 'entry-amount'}) \
            .find('input').get('value')

        self.assertEqual(first_hour_val, str(new_tco.hours_spent))
        self.assertEqual(
            len(response.html.find_all('div', {'class': 'entry'})),
            new_timecard.timecardobjects.count() + 1
        )

    def test_can_delete_unsubmitted_timecard_entries(self):
        """
        Test that entries for unsubmitted timecards can
        be deleteable (have delete checkbox inputs on page)
        """
        self.timecard.submitted = False
        self.timecard.save()

        date = self.reporting_period.start_date.strftime('%Y-%m-%d')
        response = self.app.get(
            reverse(
                'reportingperiod:UpdateTimesheet',
                kwargs={'reporting_period': date}
            ),
            headers={'X_AUTH_USER': self.user.email},
        )
        delete_divs = response.html.find_all('div', {'class': 'entry-delete'})

        self.assertTrue(len(delete_divs) > 0)
        self.assertTrue(response.context['unsubmitted'])

    def test_cannot_delete_submitted_timecard_entries(self):
        """
        Test that entries for submitted timecards cannot
        be deleted (do not have delete checkbox inputs on page)
        """
        date = self.reporting_period.start_date.strftime('%Y-%m-%d')
        response = self.app.get(
            reverse(
                'reportingperiod:UpdateTimesheet',
                kwargs={'reporting_period': date}
            ),
            headers={'X_AUTH_USER': self.user.email},
        )
        delete_divs = response.html.find_all('div', {'class': 'entry-delete'})

        self.assertEqual(len(delete_divs), 0)
        self.assertFalse(response.context['unsubmitted'])

    def test_reportperiod_updatetimesheet_save_only_set(self):
        """
        Check that save_only flag switched to True if 'save_only' in post data
        """
        date = self.reporting_period.start_date.strftime('%Y-%m-%d')
        response = self.app.post(
            reverse(
                'reportingperiod:UpdateTimesheet',
                kwargs={'reporting_period': date}
            ),
            {
                'save_only': '1',
                'timecardobjects-TOTAL_FORMS': '1',
                'timecardobjects-INITIAL_FORMS': '0',
                'timecardobjects-MIN_NUM_FORMS': '0',
                'timecardobjects-MAX_NUM_FORMS': '1000',
                'timecardobjects-0-project': '4',
                'timecardobjects-0-hours_spent': None,
            },
            headers={'X_AUTH_USER': self.regular_user.email},
        )
        formset = response.context['formset']
        self.assertTrue(formset.save_only)

    def test_report_list_not_authenticated(self):
        response = self.app.get(
            reverse('ListReportingPeriods'), expect_errors=True)
        self.assertEqual(response.status_code, 403)

    def test_create_reporting_period_superuser(self):
        periods = list(hours.models.ReportingPeriod.objects.all())
        get_res = self.app.get(
            reverse('reportingperiod:ReportingPeriodCreateView'),
            headers={'X_AUTH_USER': self.user.email},
        )
        form = get_res.forms[0]
        form['start_date'] = '07/04/2015'
        form['end_date'] = '07/11/2015'
        form['min_working_hours'] = '40'
        form['max_working_hours'] = '60'
        form.submit(headers={'X_AUTH_USER': self.user.email})
        updated_periods = list(hours.models.ReportingPeriod.objects.all())
        self.assertTrue(len(updated_periods) == len(periods) + 1)

    def test_create_reporting_period_not_superuser(self):
        response = self.app.get(
            reverse('reportingperiod:ReportingPeriodCreateView'),
            headers={'X_AUTH_USER': self.regular_user.email},
            expect_errors=True,
        )
        self.assertEqual(response.status_code, 403)

    def test_ReportingPeriodCSVView(self):
        response = self.app.get(
            reverse(
                'reports:ReportingPeriodCSVView',
                kwargs={'reporting_period': '2015-01-01'},
            )
        )
        lines = response.content.decode('utf-8').splitlines()
        self.assertEqual(len(lines), 3)
        result = '2015-01-01 - 2015-01-07,{0},aaron.snow,Peace Corps,28.00'
        self.assertEqual(
            result.format(
                self.timecard.modified.strftime('%Y-%m-%d %H:%M:%S')
            ),
            lines[1],
        )

    def test_ReportingPeriodCSVView_add_additional_row(self):
        """
        Check that adding another entry adds another row
        """
        self.timecard = hours.models.Timecard.objects.create(
            user=self.regular_user,
            submitted=True,
            reporting_period=self.reporting_period)
        self.timecard_object_1 = hours.models.TimecardObject.objects.create(
            timecard=self.timecard,
            project=self.project_1,
            hours_spent=12)

        response = self.app.get(
            reverse(
                'reports:ReportingPeriodCSVView',
                kwargs={'reporting_period': '2015-01-01'},
            )
        )
        lines = response.content.decode('utf-8').splitlines()
        self.assertEqual(len(lines), 4)

    def test_ReportingPeriodCSVView_add_additional_row_unsubmitted_time(self):
        """
        Check that adding an unsubmitted timecard DOES NOT add another row
        """
        self.timecard = hours.models.Timecard.objects.create(
            user=self.regular_user,
            submitted=False,
            reporting_period=self.reporting_period)
        self.timecard_object_1 = hours.models.TimecardObject.objects.create(
            timecard=self.timecard,
            project=self.project_1,
            hours_spent=12)

        response = self.app.get(
            reverse(
                'reports:ReportingPeriodCSVView',
                kwargs={'reporting_period': '2015-01-01'},
            )
        )
        lines = response.content.decode('utf-8').splitlines()
        self.assertEqual(len(lines), 3)

    def test_ReportingPeriodDetailView_current_employee_set_false(self):
        """ Check that the ReportingPeriodDetailView does not show users
        that have current_employee marked as false """
        response = self.app.get(
            reverse(
                'reports:ReportingPeriodDetailView',
                kwargs={'reporting_period': '2015-01-01'},
            )
        )
        self.assertEqual(
            len(response.html.find_all('tbody')), 2
        )

    def test_ReportingPeriodDetailView_add_submitted_time(self):
        """
        Check that ReportingPeriodDetailView properly allocates
        those who filled out (submitted) time vs. not
        """

        self.timecard = hours.models.Timecard.objects.create(
            user=self.regular_user,
            submitted=True,
            reporting_period=self.reporting_period
        )

        response = self.app.get(
            reverse(
                'reports:ReportingPeriodDetailView',
                kwargs={'reporting_period': '2015-01-01'},
            )
        )

        tables = response.html.find_all('table')
        not_filed_time = tables[0]
        filed_time = tables[1]
        self.assertEqual(
            len(not_filed_time.find_all('tbody')), 0
        )
        self.assertEqual(
            len(filed_time.find_all('tbody')), 2
        )


    def test_ReportingPeriodDetailView_add_unsubmitted_time(self):
        """
        Check that ReportingPeriodDetailView properly allocates
        those who filled out (submitted) time vs. not, another example
        """

        self.timecard = hours.models.Timecard.objects.create(
            user=self.regular_user,
            submitted=False,
            reporting_period=self.reporting_period
        )

        response = self.app.get(
            reverse(
                'reports:ReportingPeriodDetailView',
                kwargs={'reporting_period': '2015-01-01'},
            )
        )

        tables = response.html.find_all('table')
        not_filed_time = tables[0]
        filed_time = tables[1]

        self.assertEqual(
            len(not_filed_time.find_all('tbody')), 1
        )
        self.assertEqual(
            len(filed_time.find_all('tbody')), 1
        )

    def test_ReportingPeriodDetailView_current_employee_toggle(self):
        """ Check that changing user data attribute current_employee to
        true shows the employee on the ReportingPeriodDetailView  """
        self.former_employee.user_data.current_employee = True
        self.former_employee.user_data.save()
        response = self.app.get(
            reverse(
                'reports:ReportingPeriodDetailView',
                kwargs={'reporting_period': '2015-01-01'},
            )
        )
        self.assertEqual(
            len(response.html.find_all('tbody')), 3
        )
        self.former_employee
