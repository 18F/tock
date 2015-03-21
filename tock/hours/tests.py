from django.test import SimpleTestCase
from hours.models import ReportingPeriod, TimecardObject, Timecard
from projects.models import Project

from datetime import datetime

# Uses model-mommy (see https://model-mommy.readthedocs.org)
from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key

class ReportingPeriodTest(SimpleTestCase):

    def test_reporting_period_save(self):
        period = ReportingPeriod(start_date="2015-03-23", end_date="2015-03-27", working_hours=40)
        period.save()

        retrieved = ReportingPeriod.objects.get(pk=period.pk)
        self.assertEqual('2015-03-23', str(retrieved))

class TimecardObjectTest(SimpleTestCase):

    def test_timecardobject_save(self):
        pass

class TimecardTest(SimpleTestCase):

    def setUp(self):
        self.test_timecard = mommy.make(Timecard)
        self.project1 = mommy.make(Project)
        self.project2 = mommy.make(Project)

    def test_add_time(self):
        time1 = TimecardObject(timecard=self.test_timecard, project=self.project1, time_percentage=50)
        time2 = TimecardObject(timecard=self.test_timecard, project=self.project2, time_percentage=50)
        time1.save()
        time2.save()
        self.assertEqual(50, time1.time_percentage)