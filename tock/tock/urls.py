from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.urls import include, path

# Enable the Django admin.
from django.contrib import admin
admin.autodiscover()


def check_if_staff(user):
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    raise PermissionDenied

staff_login_required = user_passes_test(check_if_staff)
admin.site.login = staff_login_required(admin.site.login)

import hours.views
import api.urls
import projects.urls
import tock.views


urlpatterns = [
    path('', hours.views.ReportingPeriodListView.as_view(), name='ListReportingPeriods'),
    path('reporting_period/', include('hours.urls.timesheets', namespace='reportingperiod')),
    path('reports/', include('hours.urls.reports', namespace='reports')),
    path('employees/', include('employees.urls', namespace='employees')),
    path('utilization/', include('utilization.urls', namespace='utilization')),
    path('projects/', include(projects.urls)),

    # TODO: version the API?
    path('api/', include(api.urls)),

    path('admin/', admin.site.urls),

    path('auth/', include('uaa_client.urls')),

    # Trailing slash here creates unpredictable redirects in tests.
    path('logout', tock.views.logout, name='logout'),
]


# Enable Django Debug Toolbar only if in DEBUG mode.
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]


# Uncomment the next line to serve media files in dev.
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
