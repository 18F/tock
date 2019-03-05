import logging
import urllib.parse

import django.contrib.auth
from django.conf import settings
from django.shortcuts import redirect, render

logger = logging.getLogger('tock')


def csrf_failure(request, reason=""):
    logger.warn(
        'CSRF Failure for request [%s] for reason [%s]' %
        (
            request.META,
            reason
        )
    )
    return render(request, '403.html')


def logout(request):
    if request.user.is_authenticated:
        django.contrib.auth.logout(request)
        tock_logout_url = request.build_absolute_uri('logout')
        params = urllib.parse.urlencode({
            'redirect': tock_logout_url,
            'client_id': settings.UAA_CLIENT_ID,
        })
        return redirect(
            f'{settings.UAA_LOGOUT_URL}?{params}'
        )
    else:
        return render(request, 'logout.html')
