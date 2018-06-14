import urllib.parse
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User


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
