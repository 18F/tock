# -*- coding: utf-8 -*-

from django.urls import path, re_path

from api.views import ProjectList, ProjectInstanceView, UserList, ReportingPeriodList, ReportingPeriodAudit, \
    Submissions, TimecardList, hours_by_quarter, hours_by_quarter_by_user, UserDataView, FullTimecardList

urlpatterns = [
    path('projects.json', ProjectList.as_view(), name='ProjectList'),
    path('projects/<int:pk>.json', ProjectInstanceView.as_view(), name='ProjectInstanceView'),
    path('reporting_period_audit.json', ReportingPeriodList.as_view(), name='ReportingPeriodList'),
    re_path(
        r'^reporting_period_audit/(?P<reporting_period_start_date>[0-9]{4}-[0-9]{2}-[0-9]{2}).json$',
        ReportingPeriodAudit.as_view(),
        name='ReportingPeriodAudit'
    ),
    path(
        'submissions/<int:num_past_reporting_periods>.json',
        Submissions.as_view(),
        name='Submissions'
    ),
    # Note that this endpoint returns TimecardObjects
    path('timecards.json', TimecardList.as_view(), name='TimecardList'),
    # ...and this one returns Timecards (referred to as "full timecards" to disambiguate
    # from existing endpoints / naming conventions)
    path('full_timecards.json', FullTimecardList.as_view(), name='FullTimecardList'),
    path('hours/by_quarter.json', hours_by_quarter, name='HoursByQuarter'),
    path('hours/by_quarter_by_user.json', hours_by_quarter_by_user, name='HoursByQuarterByUser'),
    path('users.json', UserList.as_view(), name='UserList'),
    path('user_data.json', UserDataView.as_view(), name='UserDataView'),
]
