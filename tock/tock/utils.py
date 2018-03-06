import functools
import logging
import os
import sys

from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.permissions import BasePermission
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from tock.settings import base

logger = logging.getLogger(__name__)


class PermissionMixin(LoginRequiredMixin, object):
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
                    if isinstance(permission_class(), IsAuthenticated):
                        logger.info("User isn't logged in, redirecting...")
                        return redirect('/auth/login')
                    logger.info("User isn't allowed, redirecting...")
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
    return (
        (os.path.basename(sys.argv[0]) == 'manage.py' and
            len(sys.argv) > 1 and sys.argv[1] == 'test') or
        base.FLOAT_API_KEY == ''
    )


def flatten(nested_list):
    flat_list = []
    for sublist in nested_list:
        for item in sublist:
            flat_list.append(item)
    return flat_list
