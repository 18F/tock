from django.test import TestCase
from django.contrib.auth.models import User


class ViewsTests(TestCase):
    def test_logout_logs_user_out(self):
        user = User.objects.create_user(username='foo')
        self.client.force_login(user)

        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.context['user'].is_authenticated())
