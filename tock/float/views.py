from django.shortcuts import render
from float.models import FloatTasks
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from datetime import datetime
# Create your views here.

class FloatTaskList(ListView):
    template_name = "float/float_task_list.html"
    queryset = FloatTasks.objects.all()

    def get_context_data(self, **kwargs):
        context= super(
            FloatTaskList, self).get_context_data(**kwargs)
        context['float_tasks'] = self.queryset.filter(
            im=self.request.user.username)
        context['today'] = datetime.now()
        context['username'] = self.request.user.username
        return context
