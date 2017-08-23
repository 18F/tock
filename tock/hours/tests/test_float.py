import datetime as dt

from django.contrib.auth.models import User
from django.test import TestCase

from employees.models import UserData

from ..float import *

class FloatTests(TestCase):

    def test_find_common_weekdays(self):
        range_one = (dt.date(2017, 1, 5), dt.date(2017, 1, 10))
        range_two = (dt.date(2017, 1, 6), dt.date(2017, 1, 6))
        self.assertEqual(len(find_common_weekdays(range_one, range_two)), 1)
        range_two = (range_two[0], dt.date(2017, 9, 30))
        self.assertEqual(len(find_common_weekdays(range_one, range_two)), 3)
        range_two = (dt.date(2016, 8, 29), dt.date(2016, 9, 30))
        self.assertEqual(len(find_common_weekdays(range_one, range_two)), 0)

    def test_get_float_tasks(self):
        start_date = dt.date(2016, 10, 5)
        float_people_id = 755802
        self.assertEqual(len(get_float_tasks(start_date, float_people_id)), 2)

    def test_get_float_people_id(self):
        user = User.objects.create(username='6cfl4j.c4drwz')
        userdata = UserData.objects.create(user=user)
        # Test get from Float by Tock username.
        self.assertEqual(get_float_people_id(userdata), 755802)
        self.assertEqual(userdata.float_people_id, 755802)
        # Test get directly from UserData object.
        self.assertEqual(get_float_people_id(userdata), 755802)
        # Test return none.
        user = User.objects.create(username='tom.jones')
        userdata = UserData.objects.create(user=user)
        self.assertEqual(get_float_people_id(userdata), None)


    def test_get_float_holidays(self):
        self.assertEqual(len(get_float_holidays(dt.date(2016, 10, 1))), 1)

    def test_get_float_timeoffs(self):
        self.assertEqual(
            len(get_float_timeoffs(dt.date(2016, 10, 15), 755802)), 1)

    def test_get_work_days(self):
        holidays = []
        start_date = dt.date(2016, 10, 2)
        end_date = dt.date(2016, 10, 8)
        self.assertEqual(get_work_days(holidays, start_date, end_date), 5)
        holidays = get_float_holidays(dt.date(2016, 10, 1))
        self.assertEqual(get_work_days(holidays, start_date, end_date), 4)

    def test_get_work_hours(self):
        start_date = dt.date(2016, 10, 9)
        end_date = dt.date(2016, 10, 15)
        holidays = []
        work_days = get_work_days(holidays, start_date, end_date)
        timeoffs = []
        # Test with no timeoffs and no holidays.
        self.assertEqual(
            get_work_hours(start_date, end_date, timeoffs, work_days), 32.5)
        # Test with timeoffs and no holidays.
        timeoffs = get_float_timeoffs(dt.date(2016, 10, 15), 755802)
        self.assertEqual(
            get_work_hours(start_date, end_date, timeoffs, work_days), 13.0)
        # Test with timeoffs and holidays.
        holidays = [{'date': '2016-10-10'}]
        work_days = get_work_days(holidays, start_date, end_date)
        self.assertEqual(
            get_work_hours(start_date, end_date, timeoffs, work_days), 6.5)
        # Test with holidays and no timeoffs.
        timeoffs = []
        self.assertEqual(
            get_work_hours(start_date, end_date, timeoffs, work_days), 26.0)

    def test_get_tasks_without_holidays_without_timeoffs(self):
        start_date = dt.date(2016, 10, 9)
        end_date = dt.date(2016, 10, 15)
        float_people_id = 755802
        tasks = get_float_tasks(start_date, float_people_id)
        holidays = []
        work_days = get_work_days(holidays, start_date, end_date)
        timeoffs = []
        work_hours = get_work_hours(start_date, end_date, timeoffs, work_days)

        result = get_tasks(start_date, end_date, tasks, work_days, work_hours)
        self.assertEqual(sum([ i['hours_wk'] for i in result ]), 32.5)

    def test_get_tasks_with_holidays_without_timeoffs(self):
        start_date = dt.date(2016, 10, 9)
        end_date = dt.date(2016, 10, 15)
        float_people_id = 755802
        tasks = get_float_tasks(start_date, float_people_id)
        holidays = [{'date': '2016-10-10'}]
        work_days = get_work_days(holidays, start_date, end_date)
        timeoffs = []
        work_hours = get_work_hours(start_date, end_date, timeoffs, work_days)

        result = get_tasks(start_date, end_date, tasks, work_days, work_hours)
        self.assertEqual(sum([ i['hours_wk'] for i in result ]), 26.0)

    def test_get_tasks_with_holidays_with_timeoffs(self):
        start_date = dt.date(2016, 10, 9)
        end_date = dt.date(2016, 10, 15)
        float_people_id = 755802
        tasks = get_float_tasks(start_date, float_people_id)
        holidays = [{'date': '2016-10-10'}]
        work_days = get_work_days(holidays, start_date, end_date)
        timeoffs = get_float_timeoffs(dt.date(2016, 10, 15), 755802)
        work_hours = get_work_hours(start_date, end_date, timeoffs, work_days)

        result = get_tasks(start_date, end_date, tasks, work_days, work_hours)
        self.assertEqual(sum([ i['hours_wk'] for i in result ]), 6.5)

    def test_get_tasks_without_holidays_with_timeoffs(self):
        start_date = dt.date(2016, 10, 9)
        end_date = dt.date(2016, 10, 15)
        float_people_id = 755802
        tasks = get_float_tasks(start_date, float_people_id)
        holidays = []
        work_days = get_work_days(holidays, start_date, end_date)
        timeoffs = get_float_timeoffs(dt.date(2016, 10, 15), 755802)
        work_hours = get_work_hours(start_date, end_date, timeoffs, work_days)

        result = get_tasks(start_date, end_date, tasks, work_days, work_hours)
        self.assertEqual(sum([ i['hours_wk'] for i in result ]), 13.0)
