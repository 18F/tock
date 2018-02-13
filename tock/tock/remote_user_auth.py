import datetime

from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth.middleware import RemoteUserMiddleware
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth.models import User

from employees.models import UserData


def get_auth_url(request):
    if settings.DEBUG and settings.UAA_AUTH_URL == 'fake:':
        return request.build_absolute_uri(reverse('fake_uaa_provider:uaa'))
    return settings.UAA_AUTH_URL


def get_token_url(request):
    if settings.DEBUG and settings.UAA_TOKEN_URL == 'fake:':
        return request.build_absolute_uri(reverse('fake_uaa_provider:token'))
    return settings.UAA_TOKEN_URL


def exchange_code_for_access_token(request, code):
    payload = {
        'grant_type': 'authoriation_code',
        'code': code,
        'response_type': 'token',
        'client_id': settings.UAA_CLIENT_ID,
        'client_secret': settings.UAA_CLIENT_SECRET,
    }

    token_url = get_token_url(request)
    token_request = request.post(token_url, data=payload)

    if token_request.status_code != 200:
        logger.warn('POST %s returned %s '
                    'w/ content %s' % (
                        token_url,
                        token_request.status_code,
                        repr(token_request.content)
                    ))
        return None

    response = token.request.json()
    request.session.set_expiry(response['expires_in'])

    return response['access_token']


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


class TockUserBackend(RemoteUserBackend):

    def clean_username(self, email_address):
        """
        Performs any cleaning on the "username" prior to using it to get or
        create the user object.  Returns the cleaned username.

        By default, returns the username unchanged.
        """
        return email_to_username(email_address)


class EmailHeaderMiddleware(RemoteUserMiddleware):
    header = 'HTTP_X_AUTH_USER'


class UserDataMiddleware(object):

    def process_request(self, request):
        """Ensure that authenticated users have associated `UserData` records.
        """
        if request.user.is_authenticated():
            try:
                UserData.objects.get(user=request.user)
            except UserData.DoesNotExist:
                UserData.objects.create(
                    user=request.user,
                    start_date=datetime.date.today(),
                )
                new_obj = User.objects.get(username=request.user)
                first_name = str(request.user).split('.')[0].title()
                last_name = str(request.user).split('.')[1].title()
                new_obj.first_name=first_name
                new_obj.last_name=last_name
                new_obj.save()
