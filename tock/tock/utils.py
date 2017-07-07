import functools, datetime

from django.core.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


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

def get_fy_first_day(date):
    if date.month <= 9:
        year = (date - datetime.timedelta(weeks=52)).year
    else:
        year = date.year
    fy_first_day = datetime.date(year, 10, 1)
    return fy_first_day

def calculate_utilization(billable_hours, all_hours):
    if all_hours is (None or 0):
        return 'No hours submitted.'
    else:
        if billable_hours is None:
            return '0.00%'
        else:
            return '{:.3}%'.format((billable_hours / all_hours * 100))
