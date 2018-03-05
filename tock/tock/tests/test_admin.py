from django.test import TestCase
from django.contrib.auth.models import User


class AdminLoginTests(TestCase):
    url = '/admin/login/'

    def test_anonymous_users_are_redirected_to_uaa_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response, '/auth/login?next=/admin/login/',
            fetch_redirect_response=False)

    def test_staff_users_are_redirected_to_admin(self):
        user = User.objects.create_user(
            username='jacob', email='jacob@gsa.gov', is_staff=True)
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertRedirects(response, '/admin/')

    def test_non_staff_users_are_forbidden(self):
        user = User.objects.create_user(
            username='jacob', email='jacob@gsa.gov')
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 403)
