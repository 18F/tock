from django.urls import path, re_path

from .. import views

app_name = 'timesheets'
urlpatterns = [
    path(
        'create/', views.ReportingPeriodCreateView.as_view(), name='ReportingPeriodCreateView',
    ),
    re_path(
        r'^(?P<reporting_period>[0-9]{4}-[0-9]{2}-[0-9]{2})/$',
        views.TimecardView.as_view(),
        name='UpdateTimesheet',
    ),
    path(
        'import/',
        views.ReportingPeriodBulkImportView.as_view(),
        name='ImportReportingPeriod',
    ),
]
