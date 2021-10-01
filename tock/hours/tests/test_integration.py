import datetime

from django.urls import reverse

from django_webtest import WebTest

from test_common import ProtectedViewTestCase

from hours.forms import choice_label_for_project
import hours.models
import projects.models


class TestOptions(ProtectedViewTestCase, WebTest):

    fixtures = [
        'projects/fixtures/projects.json'
    ]

    def setUp(self):
        self.user = self.login(
            username='aaron.snow',
            is_superuser=True,
            is_staff=True
        )
        self.projects = [
            projects.models.Project.objects.get(name='openFEC'),
            projects.models.Project.objects.get(name='Peace Corps')
        ]
        self.reporting_period = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2015, 1, 7),
            exact_working_hours=40,
        )
        self.timecard = hours.models.Timecard.objects.create(
            user=self.user,
            reporting_period=self.reporting_period,
        )
        self.reporting_period2 = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2015, 1, 8),
            end_date=datetime.date(2015, 1, 14),
            exact_working_hours=40,
        )
        self.timecard2 = hours.models.Timecard.objects.create(
            user=self.user,
            reporting_period=self.reporting_period2,
        )
        self.reporting_period3 = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2015, 1, 15),
            end_date=datetime.date(2015, 1, 21),
            exact_working_hours=40,
        )

    def _assert_project_options(self, positive=None, negative=None):
        """Browse to timecard update page, then assert that positive options are
        present in select list, while negative options are absent.

        :param list positive: Positive option values
        :param list negative: Negative option values
        """
        date = self.reporting_period.start_date.strftime('%Y-%m-%d')
        url = reverse(
            'reportingperiod:UpdateTimesheet',
            kwargs={'reporting_period': date},
        )
        self.login(username='aaron.snow')
        res = self.client.get(url)
        optionTemplate = """
            <option
            value="%s"
            data-billable="billable"
            data-notes-displayed="false"
            data-notes-required="false"
            data-is_weekly_bill="false">%s</option>
        """
        for each in (positive or []):
            self.assertContains(
                res,
                optionTemplate % (each.split(' - ')[0], each),
                html=True
            )
        for each in (negative or []):
            self.assertNotContains(
                res,
                optionTemplate % (each.split(' - ')[0], each),
                html=True
            )

    def test_project_select(self):
        self._assert_project_options([
            choice_label_for_project(each) for each in self.projects
        ])

    def test_project_select_dynamic(self):
        self.projects[1].delete()
        self._assert_project_options(
            [choice_label_for_project(self.projects[0])],
            [choice_label_for_project(self.projects[1])]
        )

    def test_admin_page_reportingperiod(self):
        """ Check that admin page reportingperiod works"""
        res = self.client.get(
            reverse('admin:hours_reportingperiod_changelist')
        )
        self.assertEqual(200, res.status_code)

    def test_admin_page_timecards(self):
        """Check that admin page timecard page works"""
        timecard = hours.models.Timecard.objects.first()
        res = self.client.get(
            reverse(
                'admin:hours_timecard_change',
                args=[timecard.id],
            )
        )
        self.assertEqual(200, res.status_code)


class TestSubmit(ProtectedViewTestCase, WebTest):

    fixtures = [
        'projects/fixtures/projects.json'
    ]

    setUp = TestOptions.setUp

    def test_timecard_submit(self):
        date = self.reporting_period.start_date.strftime('%Y-%m-%d')
        url = reverse('reportingperiod:UpdateTimesheet',
                      kwargs={'reporting_period': date},)
        res = self.app.get(url, user=self.user)
        form = res.form  # only one form on the page?
        form["timecardobjects-0-project"] = self.projects[0].id
        form["timecardobjects-0-hours_spent"] = 40
        res = form.submit("submit-timecard").follow()
        self.assertEqual(200, res.status_code)
        self.assertNotContains(res, "usa-alert--error")

    def test_timecard_submit_twice(self):
        """Submit a timecard, then another one, hope for no errors."""
        date = self.reporting_period.start_date.strftime('%Y-%m-%d')
        url = reverse('reportingperiod:UpdateTimesheet',
                      kwargs={'reporting_period': date},)
        form = self.app.get(url, user=self.user).form  # only one form on the page
        form["timecardobjects-0-project"] = self.projects[0].id
        form["timecardobjects-0-hours_spent"] = 40
        form.submit("submit-timecard").follow()

        date2 = self.reporting_period2.start_date.strftime('%Y-%m-%d')
        url = reverse('reportingperiod:UpdateTimesheet',
                      kwargs={'reporting_period': date2},)
        form = self.app.get(url, user=self.user).form  # only one form on the page
        form["timecardobjects-0-project"] = self.projects[0].id
        form["timecardobjects-0-hours_spent"] = 40
        # timecard.js would set this field to be unselected, but since WebTest
        # runs no Javascript, force this field to be the empty string
        form["timecardobjects-1-project_allocation"].force_value("")
        res = form.submit("submit-timecard")

        # successful POST will give a 302 redirect
        self.assertEqual(res.status_code, 302)

class TestAdmin(ProtectedViewTestCase, WebTest):

    fixtures = [
        'projects/fixtures/projects.json'
    ]

    setUp = TestOptions.setUp

    def test_admin_weekly_bill_timecard_submit(self):
        """Test a weekly billed project via the admin interface"""
        weekly_billed_project = projects.models.Project.objects.get(name='Weekly Billing')
        url = reverse('admin:hours_timecard_add')
        res = self.app.get(url, user=self.user)
        form = res.form
        form["user"] = self.user.id
        form["reporting_period"] = "49"
        form["timecardobjects-0-project"] = weekly_billed_project.id
        form["timecardobjects-0-project_allocation"] = "1.0"
        res = form.submit("submit-timecard").follow()
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "was added successfully")
