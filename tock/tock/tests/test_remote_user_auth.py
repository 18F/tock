import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from django_webtest import WebTest

from ..remote_user_auth import email_to_username, TockUserBackend
from employees.models import UserData


class AuthTests(WebTest):

    def test_email_domain_validation(self):
        """Ensure that a given email address is a member of the right domain"""

        with self.settings(UAA_APPROVED_DOMAINS={'gsa.gov'}):
            email = 'aaron.snow@gsa.gov'
            self.assertEqual('aaron.snow', email_to_username(email))
            with self.assertRaises(ValidationError):
                email = 'aaron.snow@nasa.gov'
                email_to_username(email)

    def test_username_stripping(self):
        """Ensure that a proper username is created"""
        email = 'aaron.snow@gsa.gov'
        self.assertEqual('aaron.snow', email_to_username(email))
        email = 'aaron.snowsnowsnowsnow@gsa.gov'
        self.assertEqual('aaron.snowsnowsnowsnow', email_to_username(email))

    def _login(self, email):
        TockUserBackend.get_user_by_email(email)

    def test_login_creates_user_and_user_data(self):
        email = 'tock.tock@gsa.gov'
        self._login(email)
        user = User.objects.filter(username='tock.tock').first()

        self.assertIsNotNone(user)
        self.assertTrue(hasattr(user, 'user_data'))
        self.assertEqual('tock.tock', user.username)
        self.assertIsNotNone(UserData.objects.get(user=user))
        self.assertEqual(
            datetime.date.today(), UserData.objects.get(user=user).start_date
        )
        self.assertEqual('Tock', user.first_name)
        self.assertEqual('Tock', user.last_name)

    def test_login_ensures_user_data(self):
        email = 'tock.tock@gsa.gov'
        self._login(email)
        user = User.objects.filter(username='tock.tock').first()
        user.user_data.delete()
        user = User.objects.filter(username='tock.tock').first()
        self.assertFalse(hasattr(user, 'user_data'))
        self._login(email)
        user = User.objects.filter(username='tock.tock').first()
        self.assertTrue(hasattr(user, 'user_data'))
