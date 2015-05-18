from unittest.mock import Mock, patch

from django.conf import settings
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from employees.views import UserFormView

class UserViewTests(TestCase):

    fixtures = ['tock/fixtures/dev_user.json']
    
    def setUp(self):
        self.regular_user = get_user_model().objects.create(username="regular.user")

    def test_UserFormViewPermissionForAdmin(self):
        c = Client(HTTP_X_FORWARDED_EMAIL='test.user@gsa.gov')
        response = c.get(reverse('employees:UserFormView', args=["regular.user"]), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_UserFormViewPermissionForUser(self):
        c = Client(HTTP_X_FORWARDED_EMAIL='regular.user@gsa.gov')
        response = c.get(reverse('employees:UserFormView', args=["test.user"]), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_UserFormViewPermissionForSelf(self):
        c = Client(HTTP_X_FORWARDED_EMAIL='regular.user@gsa.gov')
        response = c.get(reverse('employees:UserFormView', args=["regular.user"]), follow=True)
        self.assertEqual(response.status_code, 200)