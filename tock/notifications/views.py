from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

class NotificationsListView(ListView):
    template_name = 'notifications/notifications_list.html'
    def get_queryset(self):
        return
