from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import auth
from django.utils.cache import add_never_cache_headers


class AutoLogout(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        fmt = '%Y%m%d%H%M%S'

        # Check if user exists and is logged in
        if request.user and request.user.is_authenticated:

            logout_time_in_seconds = settings.AUTO_LOGOUT_DELAY_MINUTES * 60

            # Compare the time of the last activity with the logout delay
            try:
                session_time = datetime.strptime(
                    request.session['tock_last_activity'],
                    fmt
                )
                if datetime.now() - session_time > \
                   timedelta(seconds=logout_time_in_seconds):
                    auth.logout(request)
                    del request.session['tock_last_activity']
                    return self.get_response(request)
            except KeyError:
                pass

        request.session['tock_last_activity'] = \
            datetime.now().strftime(fmt)

        return self.get_response(request)


class NoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        add_never_cache_headers(response)
        return response