from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(
        regex=r'^$',
        view=views.ProjectListView.as_view(),
        name='ProjectListView'
    ),
    url(
        regex=r'^(?P<pk>\d+)/$',
        view=views.ProjectView.as_view(),
        name='ProjectView'
    ),
)
