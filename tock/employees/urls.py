from django.conf.urls import url

from . import views

urlpatterns = [
    url(regex=r'^$', view=views.UserListView.as_view(), name='UserListView'),
    url(regex=r'^(?P<username>[A-Za-z0-9._%+-]*)/$',
        view=views.UserDetailView.as_view(), name='UserDetailView'),
    url(regex=r'^e/(?P<username>[A-Za-z0-9._%+-]*)/$',
        view=views.UserFormView.as_view(), name='UserFormView'),

    url(
        regex=r'^/utilization$',
        view=views.GroupUtilizationView.as_view(),
        name='GroupUtilizationView'
    )
    url(
        regex=r'^/utilization/(?P<username>[A-Za-z0-9._%+-]*)',
        view=views.UserUtilizationView.as_view(),
        name='UserUtilizationView'
    )
]
