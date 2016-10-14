from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^utilization/$',
        view=views.GroupUtilizationView.as_view(),
        name='GroupUtilizationView'
    )]