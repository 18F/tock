from django.conf.urls import url

from .. import views

urlpatterns = [
    url(regex=r'^create/$', view=views.ReportingPeriodCreateView.as_view(), name='ReportingPeriodCreateView'),
    url(regex=r'^(?P<reporting_period>[0-9]{4}-[0-9]{2}-[0-9]{2})/$', view=views.TimecardView.as_view(), name='UpdateTimesheet'),
    url(regex=r'^import/$', view=views.ReportingPeriodBulkImportView.as_view(), name='ImportReportingPeriod'),
]