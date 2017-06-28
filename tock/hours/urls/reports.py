from django.conf.urls import url

from .. import views
from api.views import ProjectList

urlpatterns = [
    url(r'^timecards_bulk.csv$', views.bulk_timecard_list, name='BulkTimecardList'),
    url(r'^slim_timecard_bulk.csv$', views.slim_bulk_timecard_list, name='SlimBulkTimecardList'),
    url(regex=r'^$', view=views.ReportsList.as_view(), name='ListReports'),
    url(regex=r'^(?P<reporting_period>[0-9]{4}-[0-9]{2}-[0-9]{2})/$',
        view=views.ReportingPeriodDetailView.as_view(), name='ReportingPeriodDetailView'),
    url(regex=r'^(?P<reporting_period>[0-9]{4}-[0-9]{2}-[0-9]{2}).csv/$',
        view=views.ReportingPeriodCSVView, name='ReportingPeriodCSVView'),
    url(regex=r'^(?P<reporting_period>[0-9]{4}-[0-9]{2}-[0-9]{2})/(?P<username>[A-Za-z0-9._%+-]*)/$',
        view=views.ReportingPeriodUserDetailView.as_view(), name='ReportingPeriodUserDetailView'),
    url(r'^project_timeline.csv$', views.project_timeline_view, name='ProjectTimelineView'),
    url(r'^user_timeline.csv$', views.user_timeline_view, name='UserTimelineView'),
    url(r'^admin_timecard_bulk.csv$', views.admin_bulk_timecard_list, name='AdminBulkTimecardList'),
    url(r'^projects.csv$', views.projects_csv, name='ProjectList'),
    url(r'^user_data.csv$', views.user_data_csv, name='UserDataView'),
    url(
        r'^general_snippets_bulk.csv$',
        views.general_snippets_only_timecard_list,
        name='GeneralSnippetsView'
    ),
    url(
        r'^dashboard/(?P<reporting_period>[0-9]{4}-[0-9]{2}-[0-9]{2})/$',
        views.DashboardView.as_view(),
        name='DashboardView'
    ),
    url(
        r'^dashboard/list$',
        view=views.DashboardReportsList.as_view(),
        name='DashboardReportsList'
    ),
]
