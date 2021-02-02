from datetime import datetime
import urllib.parse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from tock.remote_user_auth import ACCOUNT_INACTIVE_MSG

User = get_user_model()


class ViewsTests(TestCase):
    def login(self):
        user = User.objects.create_user(
            username='foo'
        )
        self.client.force_login(user)
        # Make sure we actually did the above successfully
        self.assertTrue(user.is_authenticated)

        session = self.client.session
        session['tock_last_activity'] = datetime.now().strftime('%Y%m%d%H%M%S')
        session.save()
        return user


    def test_logout_logs_user_out(self):
        ViewsTests.login(self)

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

    @override_settings(AUTO_LOGOUT_DELAY_MINUTES=1)
    def test_session_warning_expiration_soon(self):
        ViewsTests.login(self)
        response = self.client.get('/session-warning')

        self.assertEqual(response.content, b'{"warn_about_expiration":true}')

    def test_session_warning_not_expiring_yet(self):
        ViewsTests.login(self)
        response = self.client.get('/session-warning')

        self.assertEqual(response.content, b'{"warn_about_expiration":false}')

    @override_settings(AUTO_LOGOUT_DELAY_MINUTES=2)
    def test_session_warning_expiration_in_2_min(self):
        ViewsTests.login(self)
        response = self.client.get('/session-warning')

        self.assertEqual(response.content, b'{"warn_about_expiration":true}')