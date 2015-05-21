from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^projects.(?P<format>csv|json)$', views.ProjectList.as_view(), name='list_projects'),
    url(r'^users.(?P<format>csv|json)$', views.UserList.as_view(), name='list_users'),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
