from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.GroupUtilizationView.as_view(),
        name='GroupUtilizationView'
    )]
