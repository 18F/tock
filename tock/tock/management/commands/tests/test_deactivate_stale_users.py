from datetime import datetime, timedelta, timezone
from io import StringIO
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from rest_framework.authtoken.models import Token
from tock.management.commands.deactivate_stale_users import DEFAULT_STALE_DAYS

User = get_user_model()

class DeactivateStaleUsersTest(TestCase):

    def create_user(self, username, date_joined, last_login, is_active, need_token):
        user = User.objects.create_user(username, '')
        user.date_joined = date_joined
        user.last_login = last_login
        user.is_active = is_active
        user.save()

        if need_token:
            Token.objects.create(user=user)

    def assert_stdout(self, user_deactivated_count, token_removed_count, stdout):
        self.assertIn(f'deactivated {user_deactivated_count} users', stdout)
        self.assertIn(f'{DEFAULT_STALE_DAYS} days', stdout)
        self.assertIn(f'removed {token_removed_count} tokens', stdout)


    def test_deactivate_stale_user__one_active_user_with_no_token(self):
        now = datetime.now(timezone.utc)
        username = 'Jane.Doe'
        self.create_user(username,
                         now - timedelta(days=DEFAULT_STALE_DAYS + 120),
                         now - timedelta(days=DEFAULT_STALE_DAYS),
                         True,
                         False)

        before_user_count = User.objects.count()
        before_token_count = Token.objects.count()

        out = StringIO()
        call_command('deactivate_stale_users', stdout=out)
        self.assert_stdout(1, 0, out.getvalue())

        self.assertEqual(before_user_count, User.objects.count())
        self.assertEqual(before_token_count, Token.objects.count())

        updated_user = User.objects.get(username=username)
        self.assertFalse(updated_user.is_active)

        with self.assertRaises(Token.DoesNotExist):
            Token.objects.get(user=updated_user)

    def test_deactivate_stale_user__one_active_user_with_token(self):
        now = datetime.now(timezone.utc)
        username = 'John.Smith'
        self.create_user(username,
                         now - timedelta(days=DEFAULT_STALE_DAYS + 120),
                         now - timedelta(days=DEFAULT_STALE_DAYS),
                         True,
                         True)

        before_user_count = User.objects.count()
        before_token_count = Token.objects.count()

        out = StringIO()
        call_command('deactivate_stale_users', stdout=out)
        self.assert_stdout(1, 1, out.getvalue())

        self.assertEqual(before_user_count, User.objects.count())
        self.assertEqual(before_token_count - 1, Token.objects.count())

        updated_user = User.objects.get(username=username)
        self.assertFalse(updated_user.is_active)

        with self.assertRaises(Token.DoesNotExist):
            Token.objects.get(user=updated_user)

    def test_deactivate_stale_user__nonactive_user(self):
        now = datetime.now(timezone.utc)
        username = 'Long.Time'
        self.create_user(username,
                         now - timedelta(days=DEFAULT_STALE_DAYS + 120),
                         now - timedelta(days=DEFAULT_STALE_DAYS),
                         False,
                         False)

        before_user_count = User.objects.count()
        before_token_count = Token.objects.count()

        out = StringIO()
        call_command('deactivate_stale_users', stdout=out)
        self.assert_stdout(0, 0, out.getvalue())

        self.assertEqual(before_user_count, User.objects.count())
        self.assertEqual(before_token_count, Token.objects.count())

        updated_user = User.objects.get(username=username)
        self.assertFalse(updated_user.is_active)

        with self.assertRaises(Token.DoesNotExist):
            Token.objects.get(user=updated_user)

    def test_deactivate_stale_user__one_nonstale_active_user_with_token(self):
        now = datetime.now(timezone.utc)
        username = 'Mary.Wright'
        self.create_user(username,
                         now - timedelta(days=DEFAULT_STALE_DAYS + 120),
                         now,
                         True,
                         True)

        before_user_count = User.objects.count()
        before_token_count = Token.objects.count()

        out = StringIO()
        call_command('deactivate_stale_users', stdout=out)
        self.assert_stdout(0, 0, out.getvalue())

        self.assertEqual(before_user_count, User.objects.count())
        self.assertEqual(before_token_count, Token.objects.count())

        updated_user = User.objects.get(username=username)
        self.assertTrue(updated_user.is_active)

        self.assertTrue(Token.objects.get(user=updated_user))