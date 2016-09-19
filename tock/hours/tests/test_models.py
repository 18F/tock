from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase
from django.contrib.auth import get_user_model

import datetime
import hours.models
import projects.models


class ReportingPeriodTests(TestCase):
    def setUp(self):
        self.reporting_period = hours.models.ReportingPeriod(
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2015, 1, 7),
            exact_working_hours=40,
            min_working_hours=40,
            max_working_hours=60,
            message='This is not a vacation')
        self.reporting_period.save()

    def test_reporting_period_save(self):
        """Ensure that data was saved properly """
        reporting_period = hours.models.ReportingPeriod.objects.first()
        self.assertEqual(40, reporting_period.exact_working_hours)
        self.assertEqual(
            datetime.date(2015, 1, 1), reporting_period.start_date)
        self.assertEqual(datetime.date(2015, 1, 7), reporting_period.end_date)
        self.assertEqual('This is not a vacation', reporting_period.message)
        self.assertEqual(40, reporting_period.min_working_hours)
        self.assertEqual(60, reporting_period.max_working_hours)

    def test_unique_constraint(self):
        """ Check that unique constrains work for reporting period """
        with self.assertRaises(ValidationError):
            hours.models.ReportingPeriod(
                start_date=datetime.date(2015, 1, 1),
                end_date=datetime.date(2015, 1, 7),
                exact_working_hours=40).save()

    def test_get_fiscal_year(self):
        """Check to ensure the proper fiscal year is returned"""
        self.assertEqual(2015, self.reporting_period.get_fiscal_year())
        reporting_period_2 = hours.models.ReportingPeriod(
            start_date=datetime.date(2015, 10, 31),
            end_date=datetime.date(2015, 11, 7),
            exact_working_hours=32)
        self.assertEqual(2016, reporting_period_2.get_fiscal_year())


class TimecardTests(TestCase):
    fixtures = [
        'projects/fixtures/projects.json',
        'tock/fixtures/prod_user.json'
    ]

    def setUp(self):
        self.reporting_period = hours.models.ReportingPeriod.objects.create(
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2015, 1, 7),
            exact_working_hours=40)
        self.reporting_period.save()
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

    def test_time_card_saved(self):
        """ Test that the time card was saved correctly """
        timecard = hours.models.Timecard.objects.first()
        self.assertEqual(timecard.user.pk, 1)
        self.assertEqual(timecard.reporting_period.exact_working_hours, 40)
        self.assertEqual(timecard.created.day, datetime.date.today().day)
        self.assertEqual(timecard.modified.day, datetime.date.today().day)
        self.assertEqual(len(timecard.time_spent.all()), 2)

    def test_time_card_unique_constraint(self):
        """ Test that the time card model is constrained by user and reporting
        period """
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                # Prevents django.db.transaction.TransactionManagementError
                hours.models.Timecard.objects.create(
                    user=self.user,
                    reporting_period=self.reporting_period).save()

    def test_timecard_string_return(self):
        """ Ensure the returned string for the timecard is as expected"""
        self.assertEqual('aaron.snow - 2015-01-01', str(self.timecard))

    def test_timecardobject_saved(self):
        """ Check that TimeCardObject was saved properly """
        timecardobj = hours.models.TimecardObject.objects.get(
            pk=self.timecard_object_1.pk
        )
        self.assertEqual(timecardobj.timecard.user.pk, 1)
        self.assertEqual(timecardobj.project.name, 'openFEC')
        self.assertEqual(timecardobj.hours_spent, 12)
        self.assertEqual(timecardobj.created.day, datetime.date.today().day)
        self.assertEqual(timecardobj.modified.day, datetime.date.today().day)

    def test_timecardobject_hours(self):
        """ Test the TimeCardObject hours method """
        self.assertEqual(self.timecard_object_1.hours(), 12)
