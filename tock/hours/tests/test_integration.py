import datetime

from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from django_webtest import WebTest

from hours.forms import choice_label_for_project
import hours.models
import projects.models


class TestOptions(WebTest):

    fixtures = [
        'projects/fixtures/projects.json',
        'tock/fixtures/prod_user.json'
    ]

    def setUp(self):
        self.user = get_user_model().objects.get(id=1)
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
        res = self.app.get(url, headers={'X_FORWARDED_EMAIL': self.user.email})
        select = res.forms[0].fields['timecardobject_set-0-project'][0]
        options = [each[-1] for each in select.options]
        for each in (positive or []):
            self.assertIn(each, options)
        for each in (negative or []):
            self.assertNotIn(each, options)

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
        res = self.app.get(
            reverse('admin:hours_reportingperiod_changelist'),
            headers={'X_FORWARDED_EMAIL': self.user.email})
        self.assertEqual(200, res.status_code)

    def test_admin_page_timecards(self):
        """Check that admin page timecard page works"""
        timecard = hours.models.Timecard.objects.first()
        res = self.app.get(
            reverse(
                'admin:hours_timecard_change',
                args=[timecard.id],
            ),
            headers={'X_FORWARDED_EMAIL': self.user.email},
        )
        self.assertEqual(200, res.status_code)
