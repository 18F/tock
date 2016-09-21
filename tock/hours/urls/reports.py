from django.conf.urls import url

from .. import views

from api.views import bulk_timecard_list, slim_bulk_timecard_list

urlpatterns = [
    url(r'^timecards_bulk.csv$', bulk_timecard_list, name='BulkTimecardList'),
    url(r'^slim_timecard_bulk.csv$', slim_bulk_timecard_list, name='SlimBulkTimecardList'),
    url(regex=r'^$', view=views.ReportsList.as_view(), name='ListReports'),
    url(regex=r'^(?P<reporting_period>[0-9]{4}-[0-9]{2}-[0-9]{2})/$',
        view=views.ReportingPeriodDetailView.as_view(), name='ReportingPeriodDetailView'),
    url(regex=r'^(?P<reporting_period>[0-9]{4}-[0-9]{2}-[0-9]{2}).csv/$',
        view=views.ReportingPeriodCSVView, name='ReportingPeriodCSVView'),
    url(regex=r'^(?P<reporting_period>[0-9]{4}-[0-9]{2}-[0-9]{2})/(?P<username>[A-Za-z0-9._%+-]*)/$',
        view=views.ReportingPeriodUserDetailView.as_view(), name='ReportingPeriodUserDetailView'),
]
