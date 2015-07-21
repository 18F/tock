import random
import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.dateformat import format as date_format
from django_webtest import WebTest

from projects.views import project_timeline
from projects.models import Agency, Project, AccountingCode

from hours.models import ReportingPeriod, Timecard, TimecardObject


class ProjectsTest(WebTest):

    def setUp(self):
        agency = Agency(name='General Services Administration')
        agency.save()
        accounting_code = AccountingCode(
            code='abc', agency=agency, office='18F', billable=True)
        accounting_code.save()
        self.project = Project(accounting_code=accounting_code,
                               name="Test Project")
        self.project.save()

    def test_model(self):
        """ Check that the project model stores data correctly and links to
        AccountingCode model properly"""
        retrieved = Project.objects.get(pk=self.project.pk)
        self.assertEqual(
            retrieved.accounting_code.agency.name,
            'General Services Administration')
        self.assertEqual(retrieved.accounting_code.office, '18F')
        self.assertTrue(retrieved.accounting_code.billable)

    def test_is_billable(self):
        """ Check that the is_billable method works """
        retrieved = Project.objects.get(name='Test Project')
        self.assertTrue(retrieved.is_billable())
        retrieved.accounting_code.billable = False
        retrieved.accounting_code.save()
        self.assertFalse(retrieved.is_billable())

    def test_projects_list_view(self):
        """ Check that the project list view is open and the saved project
        are listed """
        response = self.app.get(reverse('ProjectListView'))
        self.assertEqual(
            len(response.html.find('a', href='/projects/1')), 1)
        self.assertEqual(response.status_code, 200)


class TestProjectTimeline(WebTest):
    fixtures = ['tock/fixtures/dev_user.json']

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
            for weeks in range(5)
        ]
        self.objs = [
            TimecardObject.objects.create(
                timecard=Timecard.objects.create(
                    user=self.user,
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

    def test_project_timeline(self):
        res = project_timeline(self.project)
        self.assertEqual(res['periods'], self.dates)
        self.assertEqual(
            res['groups'],
            {
                self.user: {
                    obj.timecard.reporting_period.start_date: obj.hours_spent
                    for obj in self.objs
                }
            },
        )

    def test_project_timeline_view(self):
        response = self.app.get(reverse('ProjectView', args=[self.project.pk]))
        table = response.html.find('table')
        self.assertEqual(
            [each.text for each in table.find_all('th')[1:]],
            [date_format(each, settings.DATE_FORMAT) for each in self.dates],
        )
        self.assertEqual(
            [each.text for each in table.find_all('td')[1:]],
            [str(float(each.hours_spent)) for each in self.objs],
        )
