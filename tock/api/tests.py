from django.test import TestCase
from django.core.urlresolvers import reverse

import csv

# common fixtures for all API tests
FIXTURES = [
    'tock/fixtures/dev_user.json',
    'projects/fixtures/projects.json',
    'hours/fixtures/timecards.json'
]

class ProjectsAPITests(TestCase):
    fixtures = FIXTURES

    def test_projects_json(self):
        pass

    def test_projects_csv(self):
        pass


class UsersAPITests(TestCase):
    fixtures = FIXTURES

    @classmethod
    def setUpClass(self):
        pass

    @classmethod
    def tearDownClass(self):
        pass

    def test_users_json(self):
        pass

    def test_users_csv(self):
        pass


class TimecardsAPITests(TestCase):
    fixtures = FIXTURES

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_timecards_json(self):
        pass

    def test_timecards_csv(self):
        pass


class ProjectTimelineTests(TestCase):
    fixtures = FIXTURES

    @classmethod
    def setUpClass(self):
        pass

    @classmethod
    def tearDownClass(self):
        pass

    def test_project_timeline(self):
        pass


class BulkTimecardsTests(TestCase):
    fixtures = FIXTURES

    def test_bulk_timecards(self):
        response = self.client.get(reverse('BulkTimecardList'))
        rows = decode_streaming_csv(response)
        expected_fields = set((
            'project_name',
            'project_id',
            'billable',
            'employee',
            'start_date',
            'end_date',
            'modified_date',
            'hours_spent',
        ))
        rows_read = 0
        for row in rows:
            self.assertEqual(set(row.keys()), expected_fields)
            self.assertEqual(row['project_id'], '1')
            rows_read += 1
        self.assertTrue(rows_read > 0, 'no rows read, expecting 1 or more')

def decode_streaming_csv(response, reader_options={}):
    lines = [line.decode('utf-8') for line in response.streaming_content]
    return csv.DictReader(lines, **reader_options)
