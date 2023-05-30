import datetime

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django_webtest import WebTest
from employees.models import UserData
from hours.models import ReportingPeriod, Timecard, TimecardObject
from organizations.models import Organization, Unit
from projects.models import AccountingCode, Agency, Project

User = get_user_model()

FIXTURES = [
    'tock/fixtures/prod_user.json',
    'projects/fixtures/projects.json',
    'hours/fixtures/timecards.json',
    'employees/fixtures/user_data.json',
]


class TestGroupUtilizationView(WebTest):
    fixtures = [
        'projects/fixtures/projects.json',
    ]

    def setUp(self):
        # Create non-billable and billable accounting codes
        # Create Timecard populated with project lines
        billable_acct = AccountingCode.objects.create(
            code='foo',
            billable=True,
            agency=Agency.objects.first()
        )

        non_billable_acct = AccountingCode.objects.create(
            code='foo',
            billable=False,
            agency=Agency.objects.first()
        )

        # Grab projects to associate with the account codes
        self.non_billable_project = Project.objects.first()
        self.non_billable_project.accounting_code = non_billable_acct
        self.non_billable_project.save()

        self.billable_project = Project.objects.get(pk=50)
        self.billable_project.accounting_code = billable_acct
        self.billable_project.save()

        self.billable_weekly_project = Project.objects.get(pk=37)
        self.billable_weekly_project.accounting_code = billable_acct
        self.billable_weekly_project.save()

        self.ooo_project = Project.objects.get(pk=1)

        test_org = Organization.objects.get_or_create(id=1)[0]
        test_unit = Unit.objects.get_or_create(org=test_org)[0]

        # create a set of users and assign them a unit from the test data
        self.user = User.objects.create(username='regular.user')
        self.user_data = UserData.objects.get_or_create(user=self.user)[0]
        self.user_data.unit = test_unit
        self.user_data.save()

        self.user_with_no_hours = User.objects.create(username='user.no.hours')
        self.user_data_no_hours = UserData.objects.get_or_create(user=self.user_with_no_hours)[0]
        self.user_data_no_hours.unit = test_unit
        self.user_data_no_hours.save()

        self.user_weekly_only = User.objects.create(username='user.weekly.only')
        self.user_data_weekly_only = UserData.objects.get_or_create(user=self.user_weekly_only)[0]
        self.user_data_weekly_only.unit = test_unit
        self.user_data_weekly_only.save()

        self.user_weekly_hourly = User.objects.create(username='user.weekly.hourly')
        self.user_data_weekly_hourly = UserData.objects.get_or_create(user=self.user_weekly_hourly)[0]
        self.user_data_weekly_hourly.unit = test_unit
        self.user_data_weekly_hourly.save()

        # These utilization tests get weird around fiscal years, this is an attempt
        # to handle things better inside of the first week to 10 days of October
        today = datetime.date.today()
        current_fy = ReportingPeriod.get_fiscal_year_from_date(today)
        fy_start_date = ReportingPeriod.get_fiscal_year_start_date(current_fy)
        safe_date = fy_start_date + datetime.timedelta(days=7)
        adjust_rp_start_date_for_fy_boundary = today < safe_date

        if adjust_rp_start_date_for_fy_boundary:
            rp_start_date = fy_start_date
        else:
            rp_start_date = datetime.date.today() - datetime.timedelta(days=7)

        self.reporting_period = ReportingPeriod.objects.create(
            start_date=rp_start_date,
            end_date=datetime.date.today()
        )

        self.rp_week_1 = ReportingPeriod.objects.create(
            start_date=datetime.date.today() - datetime.timedelta(days=14),
            end_date=datetime.date.today() - datetime.timedelta(days=8)
        )
        self.rp_week_2 = ReportingPeriod.objects.create(
            start_date=datetime.date.today() - datetime.timedelta(days=21),
            end_date=datetime.date.today() - datetime.timedelta(days=15)
        )

        # more than a year ago (outside of current fy)
        self.old_rp = ReportingPeriod.objects.create(
            start_date=datetime.date.today() - datetime.timedelta(days=385),
            end_date=datetime.date.today() - datetime.timedelta(days=379)
        )

        # create a time card with hourly billable / hourly non-billable objects
        self.timecard = Timecard.objects.create(
            reporting_period=self.reporting_period,
            user=self.user,
            submitted=True
        )

        self.nb_timecard_object = TimecardObject.objects.create(
            timecard=self.timecard,
            project=self.non_billable_project,
            hours_spent=15,
        )

        self.b_timecard_object = TimecardObject.objects.create(
            timecard=self.timecard,
            project=self.billable_project,
            hours_spent=25,
        )

        self.timecard.save()

        # create a timecard from a previous fiscal year
        self.old_timecard = Timecard.objects.create(
            reporting_period=self.old_rp,
            user=self.user_with_no_hours,
            submitted=True
        )

        self.nb_old_timecard_object = TimecardObject.objects.create(
            timecard=self.old_timecard,
            project=self.non_billable_project,
            hours_spent=15,
        )

        self.b_old_timecard_object = TimecardObject.objects.create(
            timecard=self.old_timecard,
            project=self.billable_project,
            hours_spent=25,
        )

        self.old_timecard.save()

        # a timecard with only a weekly project and non billable hourly time
        self.weekly_only_timecard = Timecard.objects.create(
            reporting_period=self.reporting_period,
            user=self.user_weekly_only,
            submitted=True
        )

        self.nb_weekly_only_timecard_object = TimecardObject.objects.create(
            timecard=self.weekly_only_timecard,
            project=self.non_billable_project,
            hours_spent=8
        )

        self.b_weekly_only_timecard_object = TimecardObject.objects.create(
            timecard=self.weekly_only_timecard,
            project=self.billable_weekly_project,
            project_allocation=1
        )

        self.weekly_only_timecard.save()

        # a timecard with billable weekly, billable hourly, and non-billable hourly
        self.weekly_hourly_timecard = Timecard.objects.create(
            reporting_period=self.reporting_period,
            user=self.user_weekly_hourly,
            submitted=True
        )

        self.bw_weekly_hourly_timecard_object = TimecardObject.objects.create(
            timecard=self.weekly_hourly_timecard,
            project=self.billable_weekly_project,
            project_allocation=.5
        )

        self.b_weekly_hourly_timecard_object = TimecardObject.objects.create(
            timecard=self.weekly_hourly_timecard,
            project=self.billable_project,
            hours_spent=12
        )

        self.nb_weekly_hourly_timecard_object = TimecardObject.objects.create(
            timecard=self.weekly_hourly_timecard,
            project=self.non_billable_project,
            hours_spent=4
        )

        self.weekly_hourly_timecard.save()


    def test_unsubmitted_card(self):
        """
        If our current timecards are unsubmitted, we should have empty data.
        """
        self.timecard.submitted = False
        self.timecard.save()
        self.weekly_only_timecard.submitted = False
        self.weekly_only_timecard.save()
        self.weekly_hourly_timecard.submitted = False
        self.weekly_hourly_timecard.save()

        response = self.app.get(
            url=reverse('utilization:GroupUtilizationView'),
            user=self.user
        )
        self.assertTrue(
            len(response.context['object_list'][0]['utilization']['last_week_data']) == 0
        )

    def test_summary_rows(self):
        """
        Row data w/ accurate total present in context
        for user created in setup.

        We'll need to submit our previously created timecard first.
        """
        response = self.app.get(
            url=reverse('utilization:GroupUtilizationView'),
            user=self.user
        )

        utilization_data = response.context['object_list'][0]['utilization']

        self.assertEqual(
            utilization_data['last_week_data'][0]['denominator'],
            self.timecard.target_hours
        )

        self.assertEqual(
            utilization_data['last_week_data'][0]['billable'],
            self.b_timecard_object.hours_spent
        )

    def test_excludes_user_with_no_recent_hours(self):
        response = self.app.get(
            url=reverse('utilization:GroupUtilizationView'),
            user=self.user
        )

        utilization_data = response.context['object_list'][0]['utilization']

        self.assertEqual(0, len([u for u in utilization_data['last_week_data'] if u['display_name'] == self.user_with_no_hours.user_data.display_name]))
        self.assertEqual(0, len([u for u in utilization_data['last_month_data'] if u['display_name'] == self.user_with_no_hours.user_data.display_name]))

    def test_includes_user_no_longer_with_unit(self):
        response = self.app.get(
            url=reverse('utilization:GroupUtilizationView'),
            user=self.user
        )

        self.user_data.unit = None

        utilization_data = response.context['object_list'][0]['utilization']

        self.assertEqual(
            utilization_data['last_week_data'][0]['denominator'],
            self.timecard.target_hours
        )

        self.assertEqual(
            utilization_data['last_week_data'][0]['billable'],
            self.b_timecard_object.hours_spent
        )

    def test_last_week_data_user_with_weekly_only(self):
        """
        Checks the utilization value for the previous week when a user
        has only weekly allocation and no billable hours.
        """
        response = self.app.get(
            url=reverse('utilization:GroupUtilizationView'),
            user=self.user_weekly_only
        )

        last_week_data = response.context['object_list'][0]['utilization']['last_week_data']

        data = [item for item in last_week_data if item['username'] == 'user.weekly.only'][0]
        self.assertEqual(data['denominator'],
            Decimal('32.0')
        )
        self.assertEqual(data['billable'],
            Decimal('32.0')
        )
        self.assertEqual(data['utilization'],
            '100%'
        )

    def test_last_month_data_user_with_weekly_and_hourly(self):
        """
        Checks the utilization value for the previous month when a user
        has weekly allocation and billable hours in their timecards.
        """
        timecard_1 = Timecard.objects.create(
            reporting_period=self.rp_week_1,
            user=self.user_weekly_hourly,
            submitted=True
        )

        TimecardObject.objects.create(
            timecard=timecard_1,
            project=self.billable_project,
            hours_spent=18,
        )

        TimecardObject.objects.create(
            timecard=timecard_1,
            project=self.ooo_project,
            hours_spent=12
        )

        TimecardObject.objects.create(
            timecard=timecard_1,
            project=self.non_billable_project,
            hours_spent=10
        )

        timecard_1.save()

        response = self.app.get(
            url=reverse('utilization:GroupUtilizationView'),
            user=self.user_weekly_hourly
        )

        last_month_data = response.context['object_list'][0]['utilization']['last_month_data']

        data = [item for item in last_month_data if item['username'] == 'user.weekly.hourly'][0]

        # 58 target hours = (80 hours in week - 8 hours OOO) * .8 billable expectation
        self.assertEqual(data['denominator'],
            Decimal('54.0')
        )
        self.assertEqual(data['billable'],
            Decimal('46.0')
        )
        self.assertEqual(data['utilization'],
            '85.2%'
        )

    def test_last_week_data_total_with_weekly_and_hourly(self):
        """
        Checks the utilization value for a unit for the previous week
        when users have both weekly allocation and billable hours. This
        test combines all of this week's timecards from the setup step.
        """
        response = self.app.get(
            url=reverse('utilization:GroupUtilizationView'),
            user=self.user_weekly_hourly
        )

        data = response.context['object_list'][0]['utilization']['last_week_totals']

        # 4 timecards * .8 billable expectation
        self.assertEqual(data['denominator'],
            Decimal('96.0')
        )
        self.assertEqual(data['billable'],
            Decimal('85.0')
        )
        self.assertEqual(data['utilization'],
            '88.5%'
        )

    def test_last_week_data_user_with_weekly_and_hourly(self):
        """
        Checks the utilization value for the previous week when a user
        has weekly allocation and billable hours.
        """
        response = self.app.get(
            url=reverse('utilization:GroupUtilizationView'),
            user=self.user_weekly_hourly
        )

        last_week_data = response.context['object_list'][0]['utilization']['last_week_data']

        data = [item for item in last_week_data if item['username'] == 'user.weekly.hourly'][0]

        self.assertEqual(data['denominator'],
            Decimal('32.0')
        )
        self.assertEqual(data['billable'],
            Decimal('28.0')
        )
        self.assertEqual(data['utilization'],
            '87.5%'
        )

    def test_user_detail_with_utilization(self):
        """UserDetail view is visible for non-billable users"""
        self.user_data.billable_expectation = 0
        self.user_data.save()

        response = self.app.get(
            url=reverse('employees:UserDetailView', args=[self.user.username]),
            user=self.user
        )

        self.assertEqual(response.status_code, 200)


class TestAnalyticsView(TestGroupUtilizationView):

    def test_analytics_view(self):

        response = self.app.get(
            url=reverse('utilization:UtilizationAnalyticsView'),
            user=self.user
        )

        self.assertEqual(response.status_code, 200)

    def test_analytics_start(self):

        response = self.app.get(
            url=reverse('utilization:UtilizationAnalyticsView') + "?after=2020-01-01",
            user=self.user
        )
        self.assertEqual(response.status_code, 200)

    def test_analytics_end(self):

        response = self.app.get(
            url=reverse('utilization:UtilizationAnalyticsView') + "?before=2020-01-01",
            user=self.user
        )
        self.assertEqual(response.status_code, 200)

    def test_analytics_start_uswds(self):
        """Specify a USWDS-format date for after."""

        response = self.app.get(
            url=reverse('utilization:UtilizationAnalyticsView') + "?after=01/01/2020",
            user=self.user
        )
        self.assertEqual(response.status_code, 200)

    def test_analytics_end_uswds(self):
        """Specify a USWDS-format date for before."""

        response = self.app.get(
            url=reverse('utilization:UtilizationAnalyticsView') + "?before=01/01/2020",
            user=self.user
        )
        self.assertEqual(response.status_code, 200)

    def test_analytics_all_orgs(self):
        response = self.app.get(
            url=reverse('utilization:UtilizationAnalyticsView') + "?org=0",
            user=self.user
        )
        self.assertContains(response, "All Organizations")

    def test_analytics_one_org(self):
        response = self.app.get(
            url=reverse('utilization:UtilizationAnalyticsView') + "?org=1",
            user=self.user
        )
        self.assertContains(response, " Organization")
