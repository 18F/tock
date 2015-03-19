from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from hours.views import WeekListView, TimecardView #, TimecardUpdateView

urlpatterns = patterns('',
    url(r'^$', WeekListView.as_view(), name='ListWeeks'),
    url(r'^timesheet/(?P<week>[\w-]+)/$', TimecardView.as_view(success_url='/'), name='UpdateTimesheet'),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

# Uncomment the next line to serve media files in dev.
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)