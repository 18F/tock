from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from tock.remote_user_auth import email_to_username


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for user in get_user_model().objects.all():
        	if '@' in user.username:
        		user.email = user.username
        		user.username = email_to_username(user.username)
        		user.save()