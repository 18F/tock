from django.views.generic import ListView
from django.views.generic.detail import DetailView

from .models import Project


class ProjectListView(ListView):
    """ View for listing all of the projects, sort projects by name """
    model = Project
    template_name = 'projects/project_list.html'

    queryset = Project.objects.all().order_by('name')

    def get_context_data(self, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)
        return context


class ProjectView(DetailView):
    """ View for listing the details of a specific project """
    model = Project
    template_name = 'projects/project_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectView, self).get_context_data(**kwargs)
        return context
