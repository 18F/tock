# -*- coding: utf-8 -*-

from django.conf.urls import url
from api import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    url(
        r'^projects.json$',
        views.ProjectList.as_view(),
        name='ProjectList'
    ),
    url(
        r'^projects/(?P<pk>\d+).json$',
        view=views.ProjectInstanceView.as_view(),
        name='ProjectInstanceView'
    ),
    url(
        r'^users.json$',
        views.UserList.as_view(),
        name='UserList'
    ),
    url(
        r'^reporting_period_audit.json$',
        view=views.ReportingPeriodList.as_view(),
        name='ReportingPeriodList'
    ),
    url(
        r'^reporting_period_audit/(?P<reporting_period_start_date>[0-9]{4}-[0-9]{2}-[0-9]{2}).json$',  # noqa
        view=views.ReportingPeriodAudit.as_view(),
        name='ReportingPeriodAudit'
    ),
    url(
        r'^timecards.json$',
        views.TimecardList.as_view(),
        name='TimecardList'
    ),
    url(
        r'^hours/by_quarter.json$',
        views.hours_by_quarter,
        name='HoursByQuarter'
    ),
    url(
        r'^hours/by_quarter_by_user.json$',
        views.hours_by_quarter_by_user,
        name='HoursByQuarterByUser'
    ),
    url(
        r'^user_data.json$',
        views.UserDataView.as_view(),
        name='UserDataView'
    ),
    url(
        r'^timecards_prefill_data.json$',
        views.TimeCardsPrefillDataListView.as_view(),
        name='TimecardsPrefillDataListView'
    ),
]
