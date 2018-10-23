import time
from django.test import TestCase, override_settings
from django.urls import reverse

from test_common import ProtectedViewTestCase


@override_settings(AUTO_LOGOUT_DELAY_MINUTES=0.05)
class MiddlewareAutoLogoutTests(ProtectedViewTestCase, TestCase):

    def test_user_auto_logged_out(self):
        self.login(username='regular.user')

        response_initial = self.client.get(reverse('ListReportingPeriods'))
        self.assertEqual(response_initial.status_code, 200)
        self.assertIn('tock_last_activity', response_initial.client.session)

        # Sleep for an arbirary five seconds
        time.sleep(5)

        response_after_expiry = self.client.get(
            reverse('ListReportingPeriods')
        )
        self.assertEqual(response_after_expiry.status_code, 302)
        self.assertIn(
            'tock_last_activity',
            response_after_expiry.client.session
        )
