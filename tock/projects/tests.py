import datetime
import random

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.utils.dateformat import format as date_format
from django_webtest import WebTest

from hours.models import ReportingPeriod, Timecard, TimecardObject
from projects.views import project_timeline
from projects.models import Agency, Project, ProjectAlert, AccountingCode


class ProjectsTest(WebTest):
    def setUp(self):
        agency = Agency(name='General Services Administration')
        agency.save()

        accounting_code = AccountingCode(
            code='abc',
            agency=agency,
            office='18F',
            billable=True
        )
        accounting_code.save()

        self.project = Project(
            accounting_code=accounting_code,
            name='Test Project',
            start_date='2016-01-01',
            end_date='2016-02-01',
            all_hours_logged = 100.00,
        )
        self.project.save()

        self.project_1 = Project.objects.create(
            accounting_code=accounting_code,
            name='Men in Black',
            active=True,
            max_hours_restriction=True,
            max_hours=38,
            all_hours_logged=37)

    def test_deactivation_when_max_hours_is_lt_all_hours(self):
        """
        Test to confirm that a project with all_hours_logged that is less
        than max_hours when max_hours_restriction is True is not deactivated
        on save().
        """
        current_active_state = self.project_1.active
        self.project_1.save()
        new_active_state = self.project_1.active
        self.assertEqual(current_active_state, new_active_state)

    def test_deactivation_when_max_hours_is_gt_all_hours(self):
        """
        Test to confirm that a project with all_hours_logged that is greater
        than max_hours when max_hours_restriction is True is deactivated on
        save().
        """
        current_active_state = self.project_1.active
        self.project_1.all_hours_logged=39
        self.project_1.save()
        new_active_state = self.project_1.active
        self.assertNotEqual(current_active_state, new_active_state)

    def test_deactivation_when_max_hours_is_et_all_hours(self):
        """
        Test to confirm that a project with all_hours_logged that is equal to
        max_hours when max_hours_restriction is True is deactivated on save().
        """
        current_active_state = self.project_1.active
        self.project_1.all_hours_logged=38
        self.project_1.save()
        new_active_state = self.project_1.active
        self.assertNotEqual(current_active_state, new_active_state)

    def test_model(self):
        """
        Check that the project model stores data correctly and links to
        AccountingCode model properly.
        """

        retrieved = Project.objects.get(pk=self.project.pk)
        self.assertEqual(
            retrieved.accounting_code.agency.name,
            'General Services Administration'
        )
        self.assertEqual(retrieved.accounting_code.office, '18F')
        self.assertEqual(retrieved.start_date, datetime.date(2016, 1, 1))
        self.assertEqual(retrieved.end_date, datetime.date(2016, 2, 1))
        self.assertTrue(retrieved.accounting_code.billable)
        self.assertNotEqual(retrieved.all_hours_logged, 101.00)

    def test_is_billable(self):
        """
        Check that the is_billable method works.
        """

        retrieved = Project.objects.get(name='Test Project')
        self.assertTrue(retrieved.is_billable())
        retrieved.accounting_code.billable = False
        retrieved.accounting_code.save()
        self.assertFalse(retrieved.is_billable())

    def test_projects_list_view(self):
        """
        Check that the project list view is open and the saved project are
        listed.
        """

        response = self.app.get(reverse('ProjectListView'))
        anchor = response.html.find(
            'a',
            href='/projects/{0}'.format(self.project.id)
        )
        self.assertIsNotNone(anchor)

    def test_projects_list_view_with_alert(self):
        """
        Check that the project list view is open and the saved project is
        listed with an alert.
        """

        project_alert = ProjectAlert(
            title='Test Alert',
            description='This is a test alert.'
        )
        project_alert.save()

        self.project.alerts.add(project_alert)

        response = self.app.get(reverse('ProjectListView'))
        span = response.html.find('span')

        self.assertIsNotNone(span)

    def test_projects_list_view_with_alert_including_url(self):
        """
        Check that the project list view is open and the saved project is
        listed with an alert that has a URL.
        """

        project_alert = ProjectAlert(
            title='Test Alert',
            description='This is a test alert.',
            destination_url='http://www.gsa.gov/'
        )
        project_alert.save()

        self.project.alerts.add(project_alert)

        response = self.app.get(reverse('ProjectListView'))
        anchor = response.html.find(
            'a',
            href='http://www.gsa.gov/'
        )
        span = response.html.find('span')

        self.assertIsNotNone(span)
        self.assertIsNotNone(anchor)

    def test_project_detail_view_with_alert(self):
        """
        Check that the project list view is open and the saved project is
        listed with an alert.
        """

        project_alert = ProjectAlert(
            title='Test Alert',
            description='This is a test alert.'
        )
        project_alert.save()

        self.project.alerts.add(project_alert)

        response = self.app.get(
            reverse('ProjectView', kwargs={'pk': self.project.id})
        )

        span = response.html.find('span')

        self.assertIsNotNone(span)

    def test_project_detail_view_with_alert_including_url(self):
        """
        Check that the project list view is open and the saved project is
        listed with an alert that has a URL.
        """

        project_alert = ProjectAlert(
            title='Test Alert',
            description='This is a test alert.',
            destination_url='http://www.gsa.gov/'
        )
        project_alert.save()

        self.project.alerts.add(project_alert)

        response = self.app.get(
            reverse('ProjectView', kwargs={'pk': self.project.id})
        )

        anchor = response.html.find(
            'a',
            href='http://www.gsa.gov/'
        )
        span = response.html.find('span')

        self.assertIsNotNone(span)
        self.assertIsNotNone(anchor)

    def test_notes_required_enables_notes_displayed(self):
        """
        Test when the notes_required attribute is enabled on a Project
        instance that the notes_displayed attribute is automatically enabled.
        """

        project = Project.objects.get(name='Test Project')
        self.assertFalse(project.notes_displayed)
        project.notes_required = True
        project.save()
        self.assertTrue(project.notes_displayed)


class ProjectAlertTests(WebTest):
    def setUp(self):
        self.alert_label = 'ALERT'
        self.alert_description = 'This is a test alert.'
        self.alert_style = ProjectAlert.INFO
        self.project_alert = ProjectAlert(
            title='Test Alert',
            description=self.alert_description,
            style=self.alert_style
        )
        self.project_alert.save()

    def test_default_string_representation(self):
        self.assertEqual('Test Alert', str(self.project_alert))

    def test_full_alert_text_without_label(self):
        self.assertEqual(self.alert_description, self.project_alert.full_alert_text)

    def test_full_alert_text_with_label(self):
        self.project_alert.label = self.alert_label
        self.project_alert.save()

        test_string = '%s: %s' % (self.alert_label, self.alert_description)
        self.assertEqual(test_string, self.project_alert.full_alert_text)

    def test_full_style(self):
        self.assertEqual(self.alert_style, self.project_alert.full_style)

    def test_full_style_with_bold(self):
        self.project_alert.style_bold = True
        self.project_alert.save()

        test_string = '%s bold' % (self.alert_style)
        self.assertEqual(test_string, self.project_alert.full_style)

    def test_full_style_with_italic(self):
        self.project_alert.style_italic = True
        self.project_alert.save()

        test_string = '%s italic' % (self.alert_style)
        self.assertEqual(test_string, self.project_alert.full_style)

    def test_full_style_with_bold_and_italic(self):
        self.project_alert.style_bold = True
        self.project_alert.style_italic = True
        self.project_alert.save()

        test_string = '%s bold italic' % (self.alert_style)
        self.assertEqual(test_string, self.project_alert.full_style)

    def test_normal_style_clears_bold_and_italic_on_save(self):
        self.project_alert.style_bold = True
        self.project_alert.style_italic = True
        self.project_alert.save()

        self.assertTrue(self.project_alert.style_bold)
        self.assertTrue(self.project_alert.style_italic)

        self.project_alert.style = ProjectAlert.NORMAL
        self.project_alert.save()

        self.assertFalse(self.project_alert.style_bold)
        self.assertFalse(self.project_alert.style_italic)


class TestProjectTimeline(WebTest):
    fixtures = ['tock/fixtures/prod_user.json']

    def setUp(self):
        super(TestProjectTimeline, self).setUp()
        self.user = User.objects.first()
        agency = Agency.objects.create(name='General Services Administration')
        accounting_code = AccountingCode.objects.create(
            code='abc',
            agency=agency,
            office='18F',
            billable=True,
        )
        self.project = Project.objects.create(
            accounting_code=accounting_code,
            name='Test Project',
        )
        self.dates = [
            datetime.date.today() + datetime.timedelta(weeks * 7)
            for weeks in range(10)
        ]
        self.objs = [
            TimecardObject.objects.create(
                timecard=Timecard.objects.create(
                    user=self.user,
                    submitted=True,
                    reporting_period=ReportingPeriod.objects.create(
                        start_date=date,
                        end_date=date + datetime.timedelta(days=6),
                    ),
                ),
                project=self.project,
                hours_spent=random.randint(5, 35),
            )
            for date in self.dates
        ]
        self.dates_recent = self.dates[-5:]
        self.objs_recent = [
            obj for obj in self.objs
            if obj.timecard.reporting_period.start_date in self.dates_recent
        ]

    def test_project_timeline(self):
        res = project_timeline(self.project)
        self.assertEqual(len(res['periods']), 5)
        self.assertEqual(res['periods'], self.dates_recent)
        self.assertEqual(
            res['groups'],
            {
                self.user: {
                    obj.timecard.reporting_period.start_date: obj.hours_spent
                    for obj in self.objs_recent
                }
            },
        )

    def test_project_timeline_diff_limit(self):
        limit = 8
        res = project_timeline(self.project, period_limit=limit)
        self.assertEqual(res['periods'], self.dates[-limit:])
        self.assertEqual(len(list(res['groups'].values())[0]), limit)

    def test_project_timeline_no_limit(self):
        res = project_timeline(self.project, period_limit=None)
        self.assertEqual(res['periods'], self.dates)
        self.assertEqual(len(list(res['groups'].values())[0]), len(self.objs))

    def test_project_timeline_view(self):
        response = self.app.get(reverse('ProjectView', args=[self.project.pk]))
        table = response.html.find('table')
        self.assertEqual(
            [each.text for each in table.find_all('th')[1:]],
            [
                date_format(each, settings.DATE_FORMAT)
                for each in self.dates_recent
            ],
        )
        self.assertEqual(
            [each.text for each in table.find_all('td')[1:]],
            [str(float(each.hours_spent)) for each in self.objs_recent],
        )


class ProjectViewTests(WebTest):
    fixtures = [
        'projects/fixtures/projects.json',
        'hours/fixtures/timecards.json',
        'tock/fixtures/prod_user.json'
    ]
    csrf_checks = False

    def test_total_hours_billed(self):
        """
        For a given project, ensure that the view displays the correct total.

        (Note that this project is the only test project for which timecards have been saved.)

        :return:
        """
        project = Project.objects.get(id__exact=1)
        timecard_objects = TimecardObject.objects.filter(
            project=project.id
        )

        total = timecard_objects.aggregate(Sum('hours_spent'))['hours_spent__sum']

        response = self.app.get(
            reverse('ProjectView', kwargs={'pk': project.id}),
            headers={'X-FORWARDED-EMAIL': 'aaron.snow@gsa.gov'}
        )

        self.assertEqual(float(response.html.select('#totalHours')[0].string), total)
