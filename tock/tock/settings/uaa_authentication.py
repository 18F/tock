import requests
import jwt
from django.contrib.auth.models import User
from django.conf import settings

def exchange_code_for_access_token(request, code):
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'response_type': 'token',
        'client_id': settings.UAA_CLIENT_ID,
        'client_secret': settings.UAA_CLIENT_SECRET
    }
    print(payload)
    token_req = requests.post(settings.UAA_TOKEN_URL, data=payload)
    if token_req.status_code != 200:

        return None

    response = token_req.json()
    print(response)
    request.session.set_expiry(response['expires_in'])

    return response['access_token']


def get_user_by_email(email):
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None

class UaaBackend:

    def authenticate(self, uaa_oauth2_code=None, request=None, **kwargs):
        if uaa_oauth2_code is None or request is None:
            return None

        access_token = exchange_code_for_access_token(request, uaa_oauth2_code)
        if access_token is None:
            return None

        user_info = jwt.decode(access_token, verify=False)

        return get_user_by_email(user_info['email'])

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
