from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from hours.views import ReportingPeriodListView, ReportingPeriodDetailView, TimecardView, ReportsList, TimecardCSVView

urlpatterns = patterns('',
    url(r'^tock/$', ReportingPeriodListView.as_view(), name='ListReportingPeriods'),
    url(r'^tock/timesheet/(?P<reporting_period>[\w-]+)/$', TimecardView.as_view(success_url='/'), name='UpdateTimesheet'),
    url(r'^tock/reports/$', ReportsList.as_view(), name='ListReports'),
    url(r'^tock/reports/(?P<reporting_period>[\w-]+)$', ReportingPeriodDetailView.as_view(), name='ReportingPeriodDetailView'),
    url(r'^tock/reports/reporting_period/(?P<reporting_period>[\w-]+).csv$', TimecardCSVView, name='TimecardCSVView'),

    # Uncomment the next line to enable the admin:
    url(r'^tock/admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^tock/__debug__/', include(debug_toolbar.urls)),
    )

# Uncomment the next line to serve media files in dev.
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)