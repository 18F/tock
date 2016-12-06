from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
import hours.models
from hours.hours_adder import HoursAdder
from employees.models import UserData
from decimal import Decimal
import datetime
import projects.models

class HoursAdderTests(TestCase):
    fixtures = [
        'projects/fixtures/projects.json',
        'tock/fixtures/prod_user.json',
    ]

    def setUp(self):
        self.reporting_period = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2015, 1, 7),
            exact_working_hours=40)
        self.user = get_user_model().objects.create(
            username='john',
            email='john@gsa.gov',
            is_superuser=False,
        )
        self.user.save()
        UserData(
            user=self.user,
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2017, 1, 1),
        ).save()

    def test_add_without_tco(self):
        project_midas = projects.models.Project.objects.get(name="Midas")
        new_period = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2016, 1, 1),
            end_date=datetime.date(2016, 1, 7),
        )
        new_timecard = hours.models.Timecard.objects.create(
            user=self.user,
            submitted=False,
            reporting_period=new_period
        )
        hours_adder = HoursAdder(
            project_id = project_midas.id,
            hours = '2',
            user_id = self.user.id,
            reporting_period_id = new_period.id,
            undo_url = ''
        )

        old_count = new_timecard.timecardobjects.count()
        hours_adder.perform_operation()
        new_count = new_timecard.timecardobjects.count()

        self.assertTrue(hours_adder.successful())
        self.assertEqual(1, new_count)

    def test_add_hours_with_existing_tco(self):
        """
        Test that addHours increases the current timecard by the
        specified amount
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
        project_midas = projects.models.Project.objects.get(name="Midas")
        new_tco = hours.models.TimecardObject.objects.create(
            timecard=new_timecard,
            project=project_midas,
            hours_spent=10.12
        )
        hours_adder = HoursAdder(
            project_id = project_midas.id,
            hours = '2',
            user_id = self.user.id,
            reporting_period_id = new_period.id,
            undo_url = ''
        )
        hours_adder.perform_operation()
        new_tco.refresh_from_db()

        self.assertTrue(hours_adder.successful())
        self.assertEqual(new_tco.hours_spent, Decimal('12.12'))
        expected_message = '2 hours have been added to Midas. <a href="?hours=-2&project=35">Undo</a>'
        self.assertEqual(expected_message, hours_adder.message)
