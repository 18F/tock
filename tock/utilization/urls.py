from django.urls import path

from .views import GroupUtilizationView, UtilizationAnalyticsView

app_name = 'utilization'
urlpatterns = [
    path('', GroupUtilizationView.as_view(), name='GroupUtilizationView'),
    path('analytics', UtilizationAnalyticsView.as_view(), name='UtilizationAnalyticsView')
]
