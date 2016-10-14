from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^utilization/$',
        view=employees.views.GroupUtilizationView.as_view(),
        name='GroupUtilizationView'
    )]