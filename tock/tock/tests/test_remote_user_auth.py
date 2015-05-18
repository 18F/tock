from unittest.mock import Mock, patch

from django.core.exceptions import ValidationError
from django.conf import settings
from django.test import TestCase

from ..remote_user_auth import email_to_username


class AuthTests(TestCase):

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