from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from django_webtest import WebTest

from ..remote_user_auth import email_to_username


class AuthTests(WebTest):

    def test_email_domain_validation(self):
        """Ensure that a given email address is a member of the right domain"""

        with self.settings(ALLOWED_EMAIL_DOMAINS={'gsa.gov'}):
            email = 'sean.herron@gsa.gov'
            self.assertEqual('sean.herron', email_to_username(email))
            with self.assertRaises(ValidationError):
                email = 'sean.herron@nasa.gov'
                email_to_username(email)

    def test_username_stripping(self):
        """Ensure that a proper username is created"""
        email = 'sean.herron@gsa.gov'
        self.assertEqual('sean.herron', email_to_username(email))
        email = 'sean.herronherronherronherron@gsa.gov'
        self.assertEqual('sean.herronherronherronherron', email_to_username(email))

    def _login(self, email):
        self.app.get(
            '/',
            headers={'X_FORWARDED_EMAIL': email},
        )

    def test_login_creates_user_and_user_data(self):
        email = 'tock@gsa.gov'
        self._login(email)
        user = User.objects.filter(username='tock').first()
        self.assertIsNotNone(user)
        self.assertTrue(hasattr(user, 'user_data'))

    def test_login_ensures_user_data(self):
        email = 'tock@gsa.gov'
        self._login(email)
        user = User.objects.filter(username='tock').first()
        user.user_data.delete()
        user = User.objects.filter(username='tock').first()
        self.assertFalse(hasattr(user, 'user_data'))
        self._login(email)
        user = User.objects.filter(username='tock').first()
        self.assertTrue(hasattr(user, 'user_data'))
