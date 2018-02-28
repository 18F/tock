import datetime
import unittest

from django.test import TestCase, override_settings
from django.contrib.auth.models import User, Group

from employees.models import UserData


@override_settings(
    PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
    AUTHENTICATION_BACKENDS=[
        'django.contrib.auth.backends.ModelBackend',
        'uaa_client.authentication.UaaBackend',
    ],
)
class BaseLoginTestCase(TestCase):

    def create_user(self, username, password=None, is_staff=False,
                    is_superuser=False, email=None, groups=()):

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )
        UserData(
            user=user,
            start_date=datetime.datetime(2014, 1, 1),
            end_date=datetime.datetime(2016, 1, 1)
        ).save()

        for groupname in groups:
            group = Group.objects.get(name=groupname)
            group.user_set.add(user)
            group.save()

        if is_staff:
            user.is_staff = True
            user.save()

        if is_superuser:
            user.is_staff = True
            user.is_superuser = True
            user.save()

        return user

    def login(self, username='first.last', is_staff=False, is_superuser=False,
              groups=(), permissions=None):

        user = self.create_user(username=username, password='example',  # nosec
                                is_staff=is_staff, is_superuser=is_superuser,
                                groups=groups)

        assert self.client.login(
            username=username,
            password='example'  # nosec
        )
        return user


class ProtectedViewTestCase(BaseLoginTestCase):

    url = None

    def assertRedirectsToLogin(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            '/auth/login/?next=%s' % url
        )

    def test_login_is_required(self):
        if not self.url:
            raise unittest.SkipTest()
        self.assertRedirectsToLogin(self.url)
