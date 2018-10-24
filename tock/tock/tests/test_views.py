import urllib.parse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from tock.remote_user_auth import ACCOUNT_INACTIVE_MSG

User = get_user_model()


class ViewsTests(TestCase):
    def test_logout_logs_user_out(self):
        user = User.objects.create_user(
            username='foo', password='bar' # nosec
        )
        self.client.force_login(user)
        # Make sure we actually did the above successfully
        self.assertTrue(user.is_authenticated)

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
