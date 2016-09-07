from django.conf.urls import patterns, url

from float import views

urlpatterns = patterns(
    '',
    url(
        regex=r'^float/$',
        view=views.FloatTaskList.as_view(),
        name='FloatData',
    ),
)
