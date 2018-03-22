import logging

from django.shortcuts import render
import django.contrib.auth

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
    django.contrib.auth.logout(request)
    return render(request, 'logout.html')


# TODO: new function signature for Django 2.0
# def handler400(request, exception, template_name='400.html'):
def handler400(request):
    response = render(
        request,
        '400.html',
        {}
    )
    response.status_code = 400
    return response


# TODO: new function signature for Django 2.0
# def handler403(request, exception, template_name='403.html'):
def handler403(request):
    response = render(
        request,
        '403.html',
        {}
    )
    response.status_code = 403
    return response


# TODO: new function signature for Django 2.0
# def handler404(request, exception, template_name='404.html'):
def handler404(request):
    response = render(
        request,
        '404.html',
        {}
    )
    response.status_code = 404
    return response


# TODO: new function signature for Django 2.0
# def handler500(request, exception, template_name='500.html'):
def handler500(request):
    response = render(
        request,
        '500.html',
        {}
    )
    response.status_code = 500
    return response
