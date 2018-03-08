import logging

from django.shortcuts import render
import django.contrib.auth

logger = logging.getLogger(__name__)


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
    django.contrib.auth.logout(request)
    return render(request, 'logout.html')
