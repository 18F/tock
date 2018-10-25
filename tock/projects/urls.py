from django.urls import path

from .views import ProjectListView, ProjectView

urlpatterns = [
    path('', ProjectListView.as_view(), name='ProjectListView'),
    path('<int:pk>/', ProjectView.as_view(), name='ProjectView'),
]
