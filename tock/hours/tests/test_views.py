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
from tock.mock_api_server import TestMockServer
from tock.settings import base, dev
from tock.utils import get_free_port
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

        self.assertIn('7.5 hours on pSOvkvbGYL', response)

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
        result = '2015-01-01 - 2015-01-07,{0},aaron.snow@gsa.gov,Peace Corps,28.00'
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
            len(response.html.find_all('tr', {'class': 'user'})), 2
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
            len(not_filed_time.find_all('tr', {'class': 'user'})), 0
        )
        self.assertEqual(
            len(filed_time.find_all('tr', {'class': 'user'})), 2
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
            len(not_filed_time.find_all('tr', {'class': 'user'})), 1
        )
        self.assertEqual(
            len(filed_time.find_all('tr', {'class': 'user'})), 1
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
            len(response.html.find_all('tr', {'class': 'user'})), 3
        )
        self.former_employee

class TestFloatViewIntegration(TestCase):
    fixtures = FIXTURES

    def setUp(self):
        self.userdata = UserData.objects.get(pk=1)

    def test_time_period(self):
        """Checks that correct time period for Float API call is derived from
        Tock reporting period."""
        pass

    def test_task_data_structure(self):
        """Checks that Float /task response data is parsed correctly."""
        port = get_free_port()
        TestMockServer.run_server(port)
        endpoint = 'tasks'
        r = requests.get(
            url='{}:{}/{}'.format(dev.FLOAT_API_URL_BASE, port, endpoint)
        )
        result = hours.views.TimecardView.clean_task_data(self, self.userdata.float_people_id, r.json())

        self.assertIn('tasks', str(result.keys()))
        self.assertIn('metadata', str(result.keys()))
        self.assertIn('float_period_end', str(result['metadata'].keys()))
        self.assertIn('days_in_float_period', str(result['metadata'].keys()))
        self.assertIn('float_period_start', str(result['metadata'].keys()))
        self.assertIn('holidays_in_float_period', str(result['metadata'].keys()))

    def test_get_float_data(self):
        """Checks that users with Float people_id information
        are handled correctly."""
        port = get_free_port()
        TestMockServer.run_server(port)
        endpoint = 'tasks'
        r = requests.get(
            url='{}:{}/{}'.format(dev.FLOAT_API_URL_BASE, port, endpoint)
        )
        float_people_id = '755802'
        result = hours.views.TimecardView.clean_task_data(self, float_people_id, r.json())

        self.assertEqual(4, len(result['tasks']))
        self.assertIn('belPvUzBnr', result['tasks'][0]['task_name'])
        self.assertEqual(7.5, result['tasks'][0]['hours_wk'])
        self.assertEqual(
            result['tasks'][0]['hours_wk'],
            float(result['tasks'][0]['hours_pd']) * base.FLOAT_API_WEEKDAYS
        )
