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
            projects.models.Project.objects.get(name='Peace Corps'),
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
            data-notes-required="false">%s</option>
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
