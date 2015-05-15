from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import hours.views

urlpatterns = patterns(
    '', url(r'^$', hours.views.home,
            name='ListReportingPeriods'),
    url(r'^reporting_period/', include("hours.urls.timesheets", namespace="reportingperiod")),
    url(r'^reports/', include("hours.urls.reports", namespace="reports")),
    url(r'^employees/', include("employees.urls", namespace="employees")),

    # Uncomment the next line to enable the admin:
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^admin/', include(admin.site.urls)),)

if settings.DEBUG:
  import debug_toolbar
  urlpatterns += patterns(
      '', url(r'^__debug__/', include(debug_toolbar.urls)),)

# Uncomment the next line to serve media files in dev.
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
