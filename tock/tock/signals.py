import logging

from django.contrib.auth.signals import user_logged_in, user_logged_out, \
    user_login_failed

logger = logging.getLogger('tock')


def successful_login(sender, request, user, **kwargs):
    logger.info(f'Successful login event for {user.username}.')


def successful_logout(sender, request, user, **kwargs):
    logger.info(f'Successful logout event for {user.username}.')

def failed_login(sender, credentials, request, **kwargs):
    logger.info(f'Unsuccessful login attempt by {credentials}.')


def setup_signals():
    user_logged_in.connect(
        successful_login,
        dispatch_uid="tock_successful_login"
    )
    user_logged_out.connect(
        successful_logout,
        dispatch_uid="tock_successful_logout"
    )
    user_login_failed.connect(
        failed_login,
        dispatch_uid="tock_failed_login"
    )
