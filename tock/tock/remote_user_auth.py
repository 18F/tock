import datetime

from uaa_client.authentication import UaaBackend
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User

from employees.models import UserData


def email_to_username(email):
    """Converts a given email address to a Django compliant username"""
    email_list = email.lower().split('@')

    # If ALLOWED_EMAIL_DOMAINS, then ensure it is in the list of domains
    if settings.ALLOWED_EMAIL_DOMAINS:
        if email_list[1] in settings.ALLOWED_EMAIL_DOMAINS:
            pass
        else:
            raise ValidationError('Email Domain not in Allowed List')

    # Return the email address with only the first 30 characters, this is the
    # username
    return email_list[0][:30]


def verify_userdata(user):
    """Ensure that authenticated users have associated `UserData` records.
    """
    try:
        user = UserData.objects.get(user=user)
    except UserData.DoesNotExist:
        UserData.objects.create(
            user=user,
            start_date=datetime.date.today(),
        )


class TockUserBackend(UaaBackend):

    def create_user_with_email(email):
        username = email_to_username(email)

        try:
            print("Try getting a user that exists already.")
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            print("Create a new user if they don't exist.")
            user = User.objects.create_user(username, email)
            verify_userdata(user)
            user.first_name = str(username).split('.')[0].title()
            user.last_name = str(username).split('.')[1].title()
            user.save()

        return user
