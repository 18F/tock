from django.urls import path

from .views import GroupUtilizationView

app_name = 'utilization'
urlpatterns = [
    path('', GroupUtilizationView.as_view(), name='GroupUtilizationView')
]