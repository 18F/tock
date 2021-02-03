import time

from django.test import TestCase, override_settings
from django.urls import reverse

from test_common import ProtectedViewTestCase


class MiddlewareAutoLogoutTests(ProtectedViewTestCase, TestCase):

    @override_settings(AUTO_LOGOUT_DELAY_MINUTES=0.05)
    def test_user_auto_logged_out(self):
        self.login(username='regular.user')

        response_initial = self.client.get(reverse('ListReportingPeriods'))
        self.assertEqual(response_initial.status_code, 200)
        self.assertIn('tock_last_activity', response_initial.client.session)

        # Sleep for five seconds
        time.sleep(5)

        response_after_expiry = self.client.get(
            reverse('ListReportingPeriods')
        )
        self.assertEqual(response_after_expiry.status_code, 302)
        self.assertIn(
            'tock_last_activity',
            response_after_expiry.client.session
        )

    def test_session_warning_does_not_update_last_activity(self):
        self.login(username='regular.user')

        initial_response = self.client.get(reverse('ListReportingPeriods'))
        last_activity = initial_response.client.session['tock_last_activity']

        time.sleep(1)

        ping_response = self.client.get(reverse('SessionWarning'))
        last_activity1 = ping_response.client.session['tock_last_activity']

        self.assertEqual(last_activity, last_activity1)
