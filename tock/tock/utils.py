import functools
import requests
import socket
import sys

from django.core.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from tock import settings
from tock.mock_api_server import TestMockServer

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

def get_float_data(endpoint, params):
    """Fetch Float data from given endpoint with given params. Different request
     variables used for testing / shell work with the fake Float API
     (see tock.mock_api_server) versus all other uses."""

    testing = 'test' in sys.argv
    shell = 'shell' in sys.argv

    if testing or shell:
        headers = settings.dev.FLOAT_API_HEADER
        port = get_free_port()
        TestMockServer.run_server(port)
        r = requests.get(
            url='{}:{}/{}'.format(settings.dev.FLOAT_API_URL_BASE, port, endpoint)
        )

    else:
        url_base = settings.base.FLOAT_API_URL_BASE
        headers = settings.base.FLOAT_API_HEADER
        r = requests.get(
            url='{}{}'.format(url_base, endpoint),
            headers=headers,
            params=params
        )

    return r

def check_status_code(r):
    if r.status_code != 200:
        return {'hard_fail':'Error connecting to Float. Please check '\
        'with #tock-dev for updates. Operation: get_task_data(). '\
        'Status code: {}'.format(
            r.status_code
            )
        }
    else:
        return r.json()

def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    address, port = s.getsockname()
    s.close()
    return port
