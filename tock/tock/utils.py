import functools
import requests
import socket
import sys

from django.core.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from tock.settings import base, dev, test

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

def get_float_data(endpoint, params=None):
    """Fetch Float data from given endpoint with given params. Different request
      variables used for testing / shell work with the fake Float API
     (see tock.mock_api_server) versus all other uses."""
    testing = 'test' in sys.argv
    shell = 'shell' in sys.argv
    if testing or shell:
        url = '{}/{}'.format(test.FLOAT_API_URL_BASE, endpoint)
        print('Fetching data from mock Float API server via {}...'.format(url))
        return requests.get(
            url=url
        )
    else:
        url = '{}/{}'.format(base.FLOAT_API_URL_BASE, endpoint)
        print('Fetching data from real Float API server via {}...'.format(url))
        return requests.get(
            url=url,
            headers=base.FLOAT_API_HEADER,
            params=params
        )
