from datetime import datetime, timedelta, timezone
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from rest_framework.authtoken.models import Token

User = get_user_model()
DEFAULT_STALE_DAYS = 90

@transaction.atomic
class Command(BaseCommand):
    help = 'Deactivate user when they have not logged in for a set amount of time'

    def add_arguments(self, parser):
        parser.add_argument('days_not_logged_in', nargs='?', type=int, default=DEFAULT_STALE_DAYS)

    @transaction.atomic
    def handle(self, *args, **options):
        now = datetime.now(timezone.utc)

        past_time = now - timedelta(days=options['days_not_logged_in'])
        user_list = User.objects.filter(last_login__lte=past_time, is_active=True)
        user_count = 0
        token_count = 0
        for user in user_list:
          user.is_active = False
          user.save()
          user_count += 1

          # There's only one token per user, filter() is used instead of get() due to cleaner implementation
          token = Token.objects.filter(user=user)
          if token:
            token.delete()
            token_count += 1

        self.stdout.write(self.style.SUCCESS(f'Found and deactivated {user_count} users who did not logged in for {options["days_not_logged_in"]} days.'))
        self.stdout.write(self.style.SUCCESS(f'Found and removed {token_count} tokens with associated users.'))