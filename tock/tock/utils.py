import functools
import requests

import sys, os

from httmock import urlmatch, HTTMock, all_requests, response

from httmock import urlmatch, HTTMock, all_requests, response

from django.core.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from tock.settings import base

class PermissionMixin(object):

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(PermissionMixin, cls).as_view(**initkwargs)

        @functools.wraps(view)
        def wrapped(request, *args, **kwargs):
            self = cls(**initkwargs)
            if hasattr(self, 'get') and not hasattr(self, 'head'):
                self.head = self.get
            self.request = request
            self.args = args
            self.kwargs = kwargs
            for permission_class in getattr(cls, 'permission_classes', ()):
                if not permission_class().has_permission(request, self):
                    raise PermissionDenied
            return view(request, args, **kwargs)
        return wrapped


class IsSuperUserOrSelf(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and (
                request.user.is_superuser or
                request.user.username == view.kwargs.get('username')
            )
        )

def is_running_test_suite():
    return (os.path.basename(sys.argv[0]) == 'manage.py' and
            len(sys.argv) > 1 and sys.argv[1] == 'test') or base.FLOAT_API_KEY == ''

def get_float_data(endpoint, params=None):
    """Fetch Float data from given endpoint with given params. Different request
      variables used for testing / shell work with the mock Float API."""

    url = '{}/{}'.format(base.FLOAT_API_URL_BASE, endpoint)

    # If testing, get mock response.
    if is_running_test_suite():
        print('Fetching data from mock Float API server via {}...'.format(url))

        def get_mock_content(path_to_content):
            with open(path_to_content) as infile:
                return infile.read()

        @all_requests
        def float_mock(url, request):
            endpoint = url.path.split('/')[-1]
            headers = {'content-type': 'application/json'}

            if endpoint == 'people':
                content = get_mock_content(
                    'employees/fixtures/float_people_fixture.json')
                return response(200, content, headers, None, 5, request)

            elif endpoint == 'tasks':
                content = get_mock_content(
                    'hours/fixtures/float_task_fixture.json')
                return response(200, content, headers, None, 5, request)

            elif endpoint == 'holidays':
                content = get_mock_content(
                    'hours/fixtures/float_holiday_fixture.json')
                return response(200, content, headers, None, 5, request)

            elif endpoint == 'timeoffs':
                content = get_mock_content(
                    'hours/fixtures/float_timeoffs_fixture.json')
                return response(200, content, headers, None, 5, request)

        with HTTMock(float_mock):
            r = requests.get(url=url)

    # Otherwise get real data from Float API.
    else:
        print('Fetching data from real Float API server via {}...'.format(url))
        r = requests.get(
            url=url,
            headers=base.FLOAT_API_HEADER,
            params=params
        )

    # Return response or log error.
    if r.status_code == 200:
        return r
    else:
        print('Failed call to Float with {}. Response:\n\n{}'.format(
            r.url, r.content))
        return None

def flatten(nested_list):
    flat_list = []
    for sublist in nested_list:
        for item in sublist:
            flat_list.append(item)
    return flat_list
