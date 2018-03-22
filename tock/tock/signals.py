import logging

from django.contrib.auth.signals import user_logged_in, user_logged_out, \
    user_login_failed
from django.dispatch import receiver

logger = logging.getLogger('tock')


@receiver(user_logged_in)
def login_logger(sender, request, user, **kwargs):
    logger.info(f'Successful login event for {user.username}.')


@receiver(user_logged_out)
def logout_logger(sender, request, user, **kwargs):
    logger.info(f'Successful logout event for {user.username}.')


@receiver(user_login_failed)
def failed_login_logger(sender, credentials, request, **kwargs):
    logger.info(f'Unsuccessful login attempt by {credentials}.')
