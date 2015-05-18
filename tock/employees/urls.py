from django.conf.urls import url

from . import views

urlpatterns = [
    url(regex=r'^$', view=views.UserListView.as_view(), name='UserListView'),
    url(regex=r'^(?P<username>[A-Za-z0-9._%+-]*)/$',
        view=views.UserFormView.as_view(), name='UserFormView'),
]
