from django.urls import path

from .views import ProjectListView, ProjectView, ProjectEngagementView

urlpatterns = [
    path('', ProjectListView.as_view(), name='ProjectListView'),
    path('<int:pk>/', ProjectView.as_view(), name='ProjectView'),
    path('engagement/', ProjectEngagementView.as_view(),
        name="ProjectEngagementView"),
]
