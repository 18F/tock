import datetime
import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError
from uaa_client.authentication import UaaBackend

from employees.models import UserData

logger = logging.getLogger('tock-auth')

ACCOUNT_INACTIVE_MSG = "Your Tock account is inactive. Please reach out to the Tock team in the #tock Slack channel for help."

def email_to_username(email):
    """Converts a given email address to a Django compliant username"""
    email_list = email.lower().split('@')

    # If UAA_APPROVED_DOMAINS, then ensure it is in the list of domains
    if settings.UAA_APPROVED_DOMAINS:
        if email_list[1] in settings.UAA_APPROVED_DOMAINS:
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
        logger.warning(
            f'Creating UserData for {user.username}.'
        )
        UserData.objects.create(
            user=user,
            start_date=datetime.date.today(),
        )


class TockUserBackend(UaaBackend):

    def user_can_authenticate(self, user):
        if not user.is_active:
            raise PermissionDenied(ACCOUNT_INACTIVE_MSG)
        return super().user_can_authenticate(user)

    @classmethod
    def get_user_by_email(cls, email):
        logger.info('Getting user for email [%s]' % email)
        user = super().get_user_by_email(email)
        if user is not None:
            logger.info(
                f'Verifying UserData for {user.username}'
            )
            verify_userdata(user)
        return user

    @classmethod
    def create_user_with_email(cls, email):
        username = email_to_username(email)

        try:
            logger.info(
                f'Fetching User for {username}'
            )
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            logger.warning(
                f'Creating User for {username}'
            )
            user = User.objects.create_user(username, email)
            user.first_name = str(username).split('.')[0].title()
            user.last_name = str(username).split('.')[1].title()
            user.save()

        return user
