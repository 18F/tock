from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from hours.views import ReportingPeriodListView, ReportingPeriodDetailView, TimecardView, ReportsList, ReportingPeriodCSVView, ReportingPeriodUserDetailView

urlpatterns = patterns('',
    url(r'^tock/$', ReportingPeriodListView.as_view(),
        name='ListReportingPeriods'),
    url(r'^tock/timesheet/(?P<reporting_period>[0-9]{4}-[0-9]{2}-[0-9]{2})/$',
        TimecardView.as_view(success_url='/'), name='UpdateTimesheet'),
    url(r'^tock/reports/$', ReportsList.as_view(), name='ListReports'),
    url(r'^tock/reports/(?P<reporting_period>[0-9]{4}-[0-9]{2}-[0-9]{2})$',
        ReportingPeriodDetailView.as_view(), name='ReportingPeriodDetailView'),
    url(r'^tock/reports/(?P<reporting_period>[0-9]{4}-[0-9]{2}-[0-9]{2}).csv$',
        ReportingPeriodCSVView, name='ReportingPeriodCSVView'),
    url(r'^tock/reports/(?P<reporting_period>[0-9]{4}-[0-9]{2}-[0-9]{2})/(?P<user>[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6})/$',
        ReportingPeriodUserDetailView.as_view(),
        name='ReportingPeriodUserDetailView'),

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