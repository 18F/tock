from django.conf.urls import url

from . import views

urlpatterns = [
    url(regex=r'^$', view=views.UserListView.as_view(), name='UserListView'),
    url(regex=r'^(?P<username>[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6})/$',
        view=views.UserFormView.as_view(), name='UserFormView'),
    url(regex=r'roster-upload/$',
        view=views.UserBulkFormView.as_view(), name='UserBulkFormView'),
]
