from django.conf import settings
from django.contrib import auth
from datetime import datetime, timedelta


class AutoLogout():
    def process_request(self, request):
        # Check if user is logged in at all
        if not request.user.is_authenticated():
            return

        fmt = '%Y%m%d%H%M%S'
        # Compare the time of the last activity with the logout delay
        try:
            session_time = datetime.strptime(
                request.session['tock_last_activity'],
                fmt
            )
            if datetime.now() - session_time > \
               timedelta(0, settings.AUTO_LOGOUT_DELAY_MINUTES * 60, 0):
                auth.logout(request)
                del request.session['tock_last_activity']
                return
        except KeyError:
            pass

        request.session['tock_last_activity'] = datetime.now().strftime(fmt)
