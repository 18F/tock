from django.conf import settings
from django.conf.urls import include, url
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

# Enable the Django admin.
from django.contrib import admin
admin.autodiscover()


def check_if_staff(user):
    if not user.is_authenticated():
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

handler400 = 'tock.views.handler400'
handler403 = 'tock.views.handler403'
handler404 = 'tock.views.handler404'
handler500 = 'tock.views.handler500'

urlpatterns = [
    url(r'^$',
        hours.views.ReportingPeriodListView.as_view(),
        name='ListReportingPeriods'),
    url(r'^reporting_period/', include(
        'hours.urls.timesheets',
        namespace='reportingperiod'
    )),
    url(r'^reports/', include(
        'hours.urls.reports',
        namespace='reports'
    )),
    url(r'^employees/', include(
        'employees.urls',
        namespace='employees'
    )),
    url(r'^utilization/', include(
        'utilization.urls',
        namespace='utilization'
    )),
    url(r'^projects/', include(projects.urls)),

    # TODO: version the API?
    url(r'^api/', include(api.urls)),

    # Enable the Django admin.
    url(r'^admin/', include(admin.site.urls)),

    url(r'^auth/', include('uaa_client.urls')),

    url(r'^logout$', tock.views.logout, name='logout'),
]


# Enable Django Debug Toolbar only if in DEBUG mode.
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]


# Uncomment the next line to serve media files in dev.
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
