import re
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import auth

class AutoLogout(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        fmt = '%Y%m%d%H%M%S'

        # Check if user exists and is logged in
        if request.user and request.user.is_authenticated:

            # Compare the time of the last activity with the logout delay
            try:
                session_time = datetime.strptime(
                    request.session['tock_last_activity'],
                    fmt
                )

                logout_time = timedelta(minutes=settings.AUTO_LOGOUT_DELAY_MINUTES) 

                if datetime.now() - session_time > logout_time:
                    auth.logout(request)
                    del request.session['tock_last_activity']
                    return self.get_response(request)
            except KeyError:
                pass

        if not re.search("session-warning", request.path):
            request.session['tock_last_activity'] = \
                datetime.now().strftime(fmt)

        return self.get_response(request)
