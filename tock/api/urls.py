from django.conf.urls import patterns, url
from api import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^projects.(?P<format>csv|json)$', views.ProjectList.as_view(), name='ProjectList'),
    url(r'^users.(?P<format>csv|json)$', views.UserList.as_view(), name='UserList'),
    url(r'^timecards.(?P<format>csv|json)$', views.TimecardList.as_view(), name='TimecardList'),
    url(r'^project_timeline.csv$', views.project_timeline_view, name='ProjectTimelineView'),
    url(r'^user_timeline.csv$', views.user_timeline_view, name='UserTimelineView'),
    url(r'^timecards_bulk.csv$', views.bulk_timecard_list, name='BulkTimecardList'),
    url(r'^hours/by_quarter.json$', views.hours_by_quarter, name='HoursByQuarter'),
    url(r'^hours/by_quarter_by_user.json$', views.hours_by_quarter_by_user, name='HoursByQuarterByUser'),
)
