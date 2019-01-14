from django.urls import path, re_path

from .. import views

app_name='reports'
urlpatterns = [
    path('timecards_bulk.csv', views.bulk_timecard_list, name='BulkTimecardList'),
    path('slim_timecard_bulk.csv', views.slim_bulk_timecard_list, name='SlimBulkTimecardList'),
    path('', views.ReportsList.as_view(), name='ListReports'),
    re_path(
        r'^(?P<reporting_period>[0-9]{4}-[0-9]{2}-[0-9]{2})/$',
        view=views.ReportingPeriodDetailView.as_view(),
        name='ReportingPeriodDetailView'
    ),
    re_path(
        r'^(?P<reporting_period>[0-9]{4}-[0-9]{2}-[0-9]{2}).csv/$',
        view=views.ReportingPeriodCSVView,
        name='ReportingPeriodCSVView'
    ),
    re_path(
        r'^(?P<reporting_period>[0-9]{4}-[0-9]{2}-[0-9]{2})/(?P<username>[A-Za-z0-9._%+-]*)/$',
        view=views.ReportingPeriodUserDetailView.as_view(),
        name='ReportingPeriodUserDetailView'
    ),
    path('project_timeline.csv', views.project_timeline_view, name='ProjectTimelineView'),
    path('user_timeline.csv', views.user_timeline_view, name='UserTimelineView'),
    path('admin_timecard_bulk.csv', views.admin_bulk_timecard_list, name='AdminBulkTimecardList'),
    path('projects.csv', views.projects_csv, name='ProjectList'),
    path('user_data.csv', views.user_data_csv, name='UserDataView'),
    path('general_snippets_bulk.csv', views.general_snippets_only_timecard_list, name='GeneralSnippetsView'),
]
