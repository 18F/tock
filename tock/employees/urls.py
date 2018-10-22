from django.urls import path

from .views import UserListView, UserDetailView, UserFormView

app_name="employees"
urlpatterns = [
    path('', UserListView.as_view(), name='UserListView'),
    path('<username>/', UserDetailView.as_view(), name='UserDetailView'),
    path('e/<username>/', UserFormView.as_view(), name='UserFormView'),
]
