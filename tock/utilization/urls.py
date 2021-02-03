from django.urls import path

from .views import GroupUtilizationView, UtilizationAnalyticsView, ProjectAnalyticsView

app_name = 'utilization'
urlpatterns = [
    path('', GroupUtilizationView.as_view(), name='GroupUtilizationView'),
    path('project/<int:project_id>/', ProjectAnalyticsView.as_view(), name='ProjectAnalyticsView'),
    path('analytics', UtilizationAnalyticsView.as_view(), name='UtilizationAnalyticsView')

]
