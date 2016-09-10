from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from django_webtest import WebTest

from tock.settings.uaa_authentication import get_user_by_email
from tock import settings

class AuthTests(WebTest):
    email = 'steven.hiller@gsa.gov'
    email_local_part = email.split('@')[0]
    email_domain_part = email.split('@')[1]

    def test_get_user_by_email(self):
        """Ensure that function splits email user name correctly."""
        actual_username = get_user_by_email(self.email)
        intended_username = User.objects.get(username='steven.hiller')
        self.assertEqual(intended_username, actual_username)

    def test_correct_allowed_email_domain(self):
        """Ensure that only users with specified email domains get access."""
        allowed_domain = ''.join(settings.base.ALLOWED_EMAIL_DOMAINS[0])
        good_email = self.email_local_part + '@' + allowed_domain
        bad_email = self.email_local_part + '@' + allowed_domain + 'x'
        self.assertIsNotNone(get_user_by_email(good_email))
        with self.assertRaises(ValidationError):
            get_user_by_email(bad_email)
