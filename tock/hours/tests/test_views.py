import datetime

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from django_webtest import WebTest
from hours.utils import number_of_hours

from employees.models import UserData
import hours.models
import projects.models
import hours.views


class UtilTests(TestCase):

    def test_number_of_hours_util(self):
        """Ensure the number of hours returns a correct value"""
        self.assertEqual(20, number_of_hours(50, 40))


class ReportTests(WebTest):
    fixtures = [
        'projects/fixtures/projects.json', 'tock/fixtures/dev_user.json']

    def setUp(self):
        self.reporting_period = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2015, 1, 7),
            working_hours=40)
        self.user = get_user_model().objects.get(id=1)
        self.timecard = hours.models.Timecard.objects.create(
            user=self.user,
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
            end_date=datetime.date(2017, 1, 1)
        ).save()

    def test_ReportList_get_queryset(self):
        hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2016, 1, 1),
            end_date=datetime.date(2016, 1, 7),
            working_hours=40)
        response = self.app.get(reverse('reports:ListReports'))
        response = response.content.decode('utf-8')
        self.assertTrue(response.index('2016') < response.index('2015'))

    def test_report_list_authenticated_without_userdata(self):
        """ Check that report list throws error when there is no user data """
        new_user = get_user_model().objects.create(
            username='new',
            email='new@gsa.gov',
        )
        has_error = False
        try:
            self.app.get(
                reverse('ListReportingPeriods'),
                headers={'X_FORWARDED_EMAIL': new_user.email},
                expect_errors=True,
            )
        except:
            has_error = True
        self.assertTrue(has_error)

    def test_report_list_authenticated_with_userdata(self):
        """ Check that main page loads with reporting periods for authenticated
        user with with userdata """
        response = self.app.get(
            reverse('ListReportingPeriods'),
            headers={'X_FORWARDED_EMAIL': self.regular_user.email},
            expect_errors=True,
        )
        self.assertEqual(response.status_code, 200)

    def test_reportperiod_updatetimesheet_self(self):
        """ Test that users can access thier own timesheets update
        forms """
        date = self.reporting_period.start_date.strftime('%Y-%m-%d')
        response = self.app.get(
            reverse(
                'reportingperiod:UpdateTimesheet',
                kwargs={'reporting_period': date}
            ),
            headers={'X_FORWARDED_EMAIL': self.regular_user.email},
        )
        self.assertEqual(response.status_code, 200)

    def test_report_list_not_authenticated(self):
        response = self.app.get(
            reverse('ListReportingPeriods'), expect_errors=True)
        self.assertEqual(response.status_code, 403)

    def test_create_reporting_period_superuser(self):
        periods = list(hours.models.ReportingPeriod.objects.all())
        get_res = self.app.get(
            reverse('reportingperiod:ReportingPeriodCreateView'),
            headers={'X_FORWARDED_EMAIL': self.user.email},
        )
        form = get_res.forms[0]
        form['start_date'] = '07/04/2015'
        form['end_date'] = '07/11/2015'
        form['working_hours'] = '40'
        form['message'] = 'always be coding'
        form.submit(headers={'X_FORWARDED_EMAIL': self.user.email})
        updated_periods = list(hours.models.ReportingPeriod.objects.all())
        self.assertTrue(len(updated_periods) == len(periods) + 1)

    def test_create_reporting_period_not_superuser(self):
        response = self.app.get(
            reverse('reportingperiod:ReportingPeriodCreateView'),
            headers={'X_FORWARDED_EMAIL': self.regular_user.email},
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
        row = response.content.decode('utf-8').splitlines()[1]
        result = '2015-01-01 - 2015-01-07,{0},test.user@gsa.gov,openFEC,12.00'
        self.assertEqual(
            result.format(
                self.timecard.modified.strftime('%Y-%m-%d %H:%M:%S')
            ),
            row,
        )
