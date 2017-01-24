from django.conf import settings
from django.conf.urls import include, url

# Enable the Django admin.
from django.contrib import admin
admin.autodiscover()

import hours.views
import api.urls
import projects.urls

urlpatterns = [
    url(r'^$',
        hours.views.ReportingPeriodListView.as_view(),
        name='ListReportingPeriods'
    ),
    url(r'^addHours/',
        hours.views.add_hours_view,
        name='AddHours'
    ),
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
]


# Enable Django Debug Toolbar only if in DEBUG mode.
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]


# Uncomment the next line to serve media files in dev.
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
