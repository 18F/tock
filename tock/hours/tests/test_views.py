import datetime
import csv

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory, override_settings
from django.urls import reverse
from django.conf import settings

from django_webtest import WebTest

from api.tests import client
from api.views import UserDataSerializer, ProjectSerializer
from employees.models import UserData, Organization
from hours.utils import number_of_hours
from hours.forms import choice_label_for_project
from hours.views import GeneralSnippetsTimecardSerializer, ReportsList

import hours.models
import projects.models

User = get_user_model()

FIXTURES = [
    'tock/fixtures/prod_user.json',
    'projects/fixtures/projects.json',
    'hours/fixtures/timecards.json',
    'employees/fixtures/user_data.json',
    'organizations/fixtures/organizations.json',
]


def decode_streaming_csv(response, **reader_options):
    lines = [line.decode('utf-8') for line in response.streaming_content]
    return list(csv.DictReader(lines, **reader_options))


class CSVTests(TestCase):
    fixtures = FIXTURES

    def test_user_data_csv(self):
        """
        Test that CSV is returned and contains the correct fields
        for user data CSV request.
        """
        response = client().get(reverse('reports:UserDataView'))
        rows = decode_streaming_csv(response)
        # Make sure we even have a response to work with.
        self.assertNotEqual(len(rows), 0)

        num_of_fields = 0
        for row in rows:
            num_of_fields = len(row)
        num_of_expected_fields = len(
            UserDataSerializer.__dict__['_declared_fields']
        )
        self.assertEqual(num_of_expected_fields, num_of_fields)

    def test_project_csv(self):
        """Test that correct fields are returned for project data CSV
        request."""
        response = client().get(reverse('reports:ProjectList'))
        rows = decode_streaming_csv(response)
        num_rows = len(rows)
        self.assertNotEqual(num_rows, 0)
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

        response = client().get(reverse('reports:GeneralSnippetsView'))
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
        response = client().get(reverse('reports:BulkTimecardList'))
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
            'expense_profit_loss_account_name',
            'employee_organization',
            'project_organization',
        ))
        rows_read = 0
        for row in rows:
            self.assertEqual(set(row.keys()), expected_fields)
            self.assertEqual(row['project_id'], '1')
            rows_read += 1
        self.assertNotEqual(rows_read, 0, 'no rows read, expecting 1 or more')

    def test_slim_bulk_timecards(self):
        response = client().get(reverse('reports:SlimBulkTimecardList'))
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
            'employee_organization',
            'project_organization',
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
            'expense_profit_loss_account_name',
            'employee_organization',
            'project_organization',
        ))
        for row in rows:
            self.assertEqual(set(row.keys()), expected_fields)

class ProjectTimelineTests(WebTest):
    fixtures = FIXTURES

    def test_project_timeline(self):
        res = client().get(reverse('reports:UserTimelineView'))
        self.assertIn(
            'aaron.snow,,2015-06-01,2015-06-08,False,20.00', str(res.content))

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
        self.client.force_login(self.user)
        response = self.client.get(reverse(
            'reports:ReportingPeriodUserDetailView',
            kwargs={'reporting_period':'1999-12-31', 'username':'aaron.snow'}
        ))
        self.assertEqual(response.context['user_utilization'], '67.5%')
        self.assertEqual(response.context['user_all_hours'], 40.00)
        self.assertEqual(response.context['user_billable_hours'], 27)
        self.assertContains(response, '67.5%')

@override_settings(STARTING_FY_FOR_REPORTS_PAGE=2015)
class ReportTests(WebTest):
    fixtures = [
        'projects/fixtures/projects.json',
        'tock/fixtures/prod_user.json',
    ]
    csrf_checks = False

    def setUp(self):
        self.start_year = settings.STARTING_FY_FOR_REPORTS_PAGE
        self.reporting_period = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(self.start_year, 1, 1),
            end_date=datetime.date(self.start_year, 1, 7),
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
            start_date=datetime.date(self.start_year, 1, 1),
            end_date=datetime.date(self.start_year + 2, 1, 1),
        ).save()
        self.former_employee = get_user_model().objects.create(
            username='maya',
            email='maya@gsa.gov',
            is_superuser=False,
        )
        self.regular_user.save()
        UserData(
            user=self.former_employee,
            start_date=datetime.date(self.start_year, 1, 1),
            end_date=datetime.date(self.start_year + 2, 1, 1),
            current_employee=False,
        ).save()

    def test_ReportList_get_queryset(self):
        """
        Provide a sorted list of (FY, [reporting_periods]) after
        settings.STARTING_FY_FOR_REPORTS_PAGE
        """
        # This old report Should not be included in results
        old_report, _ = hours.models.ReportingPeriod.objects.get_or_create(
            start_date=datetime.date(self.start_year - 2, 1, 1),
            end_date=datetime.date(self.start_year - 1, 1, 7),
        exact_working_hours=40)
        self.assertEqual(len(ReportsList().get_queryset()), 1)

        new_report, _ = hours.models.ReportingPeriod.objects.get_or_create(
            start_date=datetime.date(self.start_year + 1, 1, 1),
            end_date=datetime.date(self.start_year + 2, 1, 7),
        exact_working_hours=40)
        self.assertEqual(len(ReportsList().get_queryset()), 2)

    def test_ReportList_get_context_data(self):
        """fiscal_years and starting_report_date are added to context"""
        context = self.app.get(reverse('reports:ListReports'), user=self.user).context
        self.assertIn('fiscal_years', context)
        self.assertIn('starting_report_date', context)

    def test_ReportList_excludes_dates_before_setting(self):
        """
        ReportList returns only objects which take place
        after `settings.STARTING_FY_FOR_REPORTS_PAGE`
        """
        hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(self.start_year - 2, 1, 1),
            end_date=datetime.date(self.start_year - 1, 1, 7),
            exact_working_hours=40)
        response = self.app.get(reverse('reports:ListReports'), user=self.user)
        self.assertNotContains(response, str(self.start_year - 2))

    def test_report_list_authenticated(self):
        """ Check that main page loads with reporting periods for authenticated
        user with with userdata """
        response = self.app.get(
            reverse('ListReportingPeriods'),
            user=self.regular_user,
        )
        self.assertEqual(response.status_code, 200)

    def test_auto_create_reporting_period(self):
        """ Check that a reporting period is automatically created if the
        previous reporting period has ended. """
        existing_rps = hours.models.ReportingPeriod.objects.all()
        self.app.get(
            reverse('ListReportingPeriods'),
            user=self.regular_user,
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
        self.app.get(
            reverse('ListReportingPeriods'),
            user=self.regular_user,
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
            self.app.get(
                reverse('ListReportingPeriods'),
                user=self.regular_user,
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
            self.app.get(
                reverse('ListReportingPeriods'),
                user=self.regular_user,
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
            self.app.get(
                reverse('ListReportingPeriods'),
                user=self.regular_user,
            )
            ct_new_rps = len(hours.models.ReportingPeriod.objects.all())
            self.assertNotEqual(ct_existing_rps, ct_new_rps)

    def test_dont_auto_create_rp(self):
        """ Check that a new reporting period is NOT created if the current
        reporting period has not ended. """
        ct_existing_rps = len(hours.models.ReportingPeriod.objects.all())
        today = datetime.datetime.utcnow().date()
        self.reporting_period.start_date = today
        self.reporting_period.end_date = today + datetime.timedelta(days=1)
        self.reporting_period.save()
        self.app.get(
            reverse('ListReportingPeriods'),
            user=self.regular_user,
        )
        ct_new_rps = len(hours.models.ReportingPeriod.objects.all())
        self.assertEqual(ct_existing_rps, ct_new_rps)

    def test_dont_auto_create_rp_if_no_rps(self):
        """ Check that no attempt to auto-create a reporting period is made
        if no reporting periods exist. """
        self.reporting_period.delete()
        self.app.get(
            reverse('ListReportingPeriods'),
            user=self.regular_user,
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
            user=self.regular_user,
        )
        self.assertEqual(response.status_code, 200)

    def test_reportperiod_updatetimesheet_no_reportperiod(self):
        """
        Tests that a 404 is raised when a reporting period is not found.
        """
        date = datetime.date(1980, 10, 1).strftime('%Y-%m-%d')
        response = self.app.get(
            reverse(
                'reportingperiod:UpdateTimesheet',
                kwargs={'reporting_period': date}
            ),
            user=self.regular_user,
            expect_errors=True
        )
        self.assertEqual(response.status_code, 404)

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
            user=self.user,
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
            user=self.user,
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
            user=self.user,
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
            user=self.user,
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
            user=self.user,
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
            user=self.user,
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
            params={
                'save_only': '1',
                'timecardobjects-TOTAL_FORMS': '1',
                'timecardobjects-INITIAL_FORMS': '0',
                'timecardobjects-MIN_NUM_FORMS': '0',
                'timecardobjects-MAX_NUM_FORMS': '1000',
                'timecardobjects-0-project': '4',
                'timecardobjects-0-hours_spent': None,
            },
            user=self.regular_user,
        )
        formset = response.context['formset']
        self.assertTrue(formset.save_only)

    def test_report_list_not_authenticated(self):
        response = self.app.get(
            reverse('ListReportingPeriods'))
        self.assertRedirects(response, '/auth/login',
                             fetch_redirect_response=False)

    def test_create_reporting_period_superuser(self):
        periods = list(hours.models.ReportingPeriod.objects.all())
        get_res = self.app.get(
            reverse('reportingperiod:ReportingPeriodCreateView'),
            user=self.user,
        )
        form = get_res.forms[0]
        form['start_date'] = '07/04/2015'
        form['end_date'] = '07/11/2015'
        form['min_working_hours'] = '40'
        form['max_working_hours'] = '60'
        form.submit(user=self.user)
        updated_periods = list(hours.models.ReportingPeriod.objects.all())
        self.assertTrue(len(updated_periods) == len(periods) + 1)

    def test_create_reporting_period_not_superuser(self):
        response = self.app.get(
            reverse('reportingperiod:ReportingPeriodCreateView'),
            user=self.regular_user,
            expect_errors=True,
        )
        self.assertEqual(response.status_code, 403)

    def test_ReportingPeriodCSVView(self):
        """
        CSV row representation of included TimeCardObjects
        must be present in generated CSV
        """
        reporting_period = '2015-01-01'
        expected = hours.models.TimecardObject.objects.filter(
            timecard__reporting_period__start_date=reporting_period
        ).first()
        response = self.app.get(
            reverse(
                'reports:ReportingPeriodCSVView',
                kwargs={'reporting_period': reporting_period},
            ),
            user=self.regular_user
        )
        lines = response.content.decode('utf-8').splitlines()
        self.assertEqual(len(lines), 3)
        # coerce to comma delimited string for comparison
        expected_csv_row = ','.join([str(x) for x in expected.to_csv_row()])
        self.assertIn(expected_csv_row, lines)

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
            ),
            user=self.regular_user
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
            ),
            user=self.regular_user
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
            ),
            user=self.regular_user
        )
        self.assertEqual(
            len(response.html.find_all('tbody')), 2
        )

    def test_ReportingPeriodDetailView_invalid_date_404(self):
        response = self.app.get(
            reverse(
                'reports:ReportingPeriodDetailView',
                kwargs={'reporting_period': '1776-07-04'},
            ),
            user=self.regular_user,
            expect_errors=True
        )
        self.assertEqual(response.status_code, 404)

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
            ),
            user=self.regular_user
        )
        self.assertEqual(len(response.context['users_without_filed_timecards']), 0)
        self.assertEqual(len(response.context['timecard_list']), 2)

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
            ),
            user=self.regular_user
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
            ),
            user=self.regular_user
        )
        self.assertContains(response,
            '<td><a href="mailto:maya@gsa.gov">maya@gsa.gov</td>')

    def test_ReportingPeriodDetailView_shows_organization(self):
        """Report detail tables must show each user's organization"""
        self.regular_user.user_data.organization = Organization.objects.get_or_create(name='TEST_ORG')[0]
        self.regular_user.user_data.save()
        response = self.app.get(
            reverse(
                'reports:ReportingPeriodDetailView',
                kwargs={'reporting_period': '2015-01-01'},
            ),
            user=self.regular_user
        )

        self.assertContains(response,
                            self.regular_user.user_data.organization)

class PrefillDataViewTests(WebTest):
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
        self.timecard_1 = hours.models.Timecard.objects.create(
            reporting_period=self.rp_1,
            user=self.user
        )
        self.timecard_2 = hours.models.Timecard.objects.create(
            reporting_period=self.rp_2,
            user=self.user
        )

        self.project_1 = projects.models.Project.objects.first()
        self.project_1.save()
        self.project_2 = projects.models.Project.objects.last()
        self.project_2.save()

        self.pfd1 = hours.models.TimecardPrefillData.objects.create(
            employee=self.ud,
            project=self.project_2,
            hours=Decimal('10.40')
        )
        self.pfd1.save()

        self.pfd2 = hours.models.TimecardPrefillData.objects.create(
            employee=self.ud,
            project=self.project_1,
            hours=Decimal('10.40'),
            is_active=False
        )
        self.pfd2.save()

    def test_active_prefills_added_to_timecard(self):
        response = self.app.get(
            reverse(
                'reportingperiod:UpdateTimesheet',
                kwargs={'reporting_period': self.rp_1.start_date}
            ),
            user=self.user,
        )

        # Only our prefilled object should appear in this form.
        self.assertEqual(len(response.context['formset'].forms), 1)

        form = response.context['formset'].forms[0]

        # Check that our prefill information is what we expect it to be.
        self.assertEqual(form.initial['project'], self.pfd1.project.id)
        self.assertEqual(
            form.initial['hours_spent'],
            self.pfd1.hours
        )

    def test_active_prefills_added_to_timecard_pulling_existing_timecard_info(self):
        tco = hours.models.TimecardObject.objects.create(
            timecard=self.timecard_1,
            project=self.project_1,
            hours_spent=Decimal('25.00')
        )
        self.timecard_1.submitted = True
        self.timecard_1.save()

        response = self.app.get(
            reverse(
                'reportingperiod:UpdateTimesheet',
                kwargs={'reporting_period': self.rp_2.start_date}
            ),
            user=self.user,
        )

        # Only our prefilled object should appear in this form.
        self.assertEqual(len(response.context['formset'].forms), 2)

        prefill = response.context['formset'].forms[0]
        previous = response.context['formset'].forms[1]

        # Check that our prefill information is what we expect it to be.
        self.assertEqual(prefill.initial['project'], self.pfd1.project.id)
        self.assertEqual(
            prefill.initial['hours_spent'],
            self.pfd1.hours
        )

        # Check that our previous timecard entry is carried over as well, but
        # without any hours.
        self.assertEqual(previous.initial['project'], tco.project.id)
        self.assertEqual(previous.initial['hours_spent'], None)

    def test_active_prefills_fill_in_hours_from_previous_timecard(self):
        tco_1 = hours.models.TimecardObject.objects.create(
            timecard=self.timecard_1,
            project=self.project_1,
            hours_spent=Decimal('25.00')
        )
        hours.models.TimecardObject.objects.create(
            timecard=self.timecard_1,
            project=self.project_2,
            hours_spent=Decimal('15.00')
        )
        self.timecard_1.submitted = True
        self.timecard_1.save()

        response = self.app.get(
            reverse(
                'reportingperiod:UpdateTimesheet',
                kwargs={'reporting_period': self.rp_2.start_date}
            ),
            user=self.user,
        )

        # Only our prefilled object should appear in this form.
        # NOTE:  includes empty form
        self.assertEqual(len(response.context['formset'].forms), 3)

        prefill = response.context['formset'].forms[0]
        previous = response.context['formset'].forms[1]

        # Check that our prefill information is what we expect it to be.
        self.assertEqual(prefill.initial['project'], self.pfd1.project.id)
        self.assertEqual(
            prefill.initial['hours_spent'],
            self.pfd1.hours
        )

        # Check that our previous timecard entry is carried over as well, but
        # without any hours.
        self.assertEqual(previous.initial['project'], tco_1.project.id)
        self.assertEqual(previous.initial['hours_spent'], None)


    def test_active_prefills_not_added_to_existing_timecards(self):
        tco = hours.models.TimecardObject.objects.create(
            timecard=self.timecard_1,
            project=self.project_1,
            hours_spent=Decimal('25.00')
        )

        response = self.app.get(
            reverse(
                'reportingperiod:UpdateTimesheet',
                kwargs={'reporting_period': self.rp_1.start_date}
            ),
            user=self.user,
        )

        # Only the existing timecard object should appear in this form; no
        # prefill data
        # NOTE:  includes empty form
        self.assertEqual(len(response.context['formset'].forms), 2)

        form = response.context['formset'].forms[0]

        # Check that our existing information is what we expect it to be.
        self.assertEqual(form.initial['project'], tco.project.id)
        self.assertEqual(form.initial['hours_spent'], tco.hours_spent)
