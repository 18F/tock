from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.conf import settings

from django.contrib.auth.models import User
from projects.models import Project
from hours.models import TimecardObject

class ProjectsAPITests(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_projects_json(self):
        pass

    def test_projects_csv(self):
        pass


class UsersAPITests(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_users_json(self):
        pass

    def test_users_csv(self):
        pass


class TimecardsAPITests(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_timecards_json(self):
        pass

    def test_timecards_csv(self):
        pass


class ProjectTimelineTests(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_project_timeline(self):
        pass


class BulkTimecardsTests(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_bulk_timecards(self):
        pass


