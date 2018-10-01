import urllib.parse

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from tock.remote_user_auth import ACCOUNT_INACTIVE_MSG


class ViewsTests(TestCase):
    def test_logout_logs_user_out(self):
        user = User.objects.create_user(username='foo')
        self.client.force_login(user)

        uaa_redirect_url = settings.UAA_LOGOUT_URL
        uaa_redirect_url += '?'
        uaa_redirect_url += urllib.parse.urlencode({
            'redirect': 'http://testserver/logout',
            'client_id': settings.UAA_CLIENT_ID,
        })

        self.assertFalse(self.client.session.is_empty())
        response = self.client.get('/logout')
        self.assertRedirects(
            response,
            uaa_redirect_url,
            fetch_redirect_response=False
        )
        self.assertTrue(self.client.session.is_empty())

    def test_inactive_user_denied(self):
        """Inactive users cannot access Tock"""
        user = User.objects.create_user(username='foo', is_active=False)
        self.client.force_login(user)
        r = self.client.get('/')
        self.assertContains(r, ACCOUNT_INACTIVE_MSG, status_code=403)
