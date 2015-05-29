from django.shortcuts import render

from django.conf import settings
from django.shortcuts import render, resolve_url
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.views.generic import ListView
from django.views.generic.detail import DetailView

from tock.remote_user_auth import email_to_username

from .models import Project, Agency

class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'

    # order the projects alphabetically, rather than by
    # insert (or PK?) order
    queryset = Project.objects.all().order_by('name')

    def get_context_data(self, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)
        return context

class ProjectView(DetailView):
    model = Project
    template_name = 'projects/project_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectView, self).get_context_data(**kwargs)
        return context
