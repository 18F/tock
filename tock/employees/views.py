from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.views.generic import ListView
from django.views.generic.edit import FormView
from django.core import exceptions
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test

from .forms import UserForm

from .models import UserData

# Create your views here.
class UserListView(ListView):
    model = User
    template_name = 'employees/user_list.html'


class UserFormView(FormView):
    template_name = 'employees/user_form.html'
    form_class = UserForm

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(UserFormView, self).dispatch(*args, **kwargs)
    
    def get_initial(self):
        initial = super(UserFormView, self).get_initial()
        user, created = User.objects.get_or_create(username=self.kwargs['username'])
        initial['email'] = user.username
        initial['first_name'] = user.first_name
        initial['last_name'] = user.last_name

        if hasattr(user, 'user_data'):
            initial['start_date'] = user.user_data.start_date
            initial['end_date'] = user.user_data.end_date

        return initial

    def form_valid(self, form):
        if form.is_valid():
            user, created = User.objects.get_or_create(username=self.kwargs['username'])
            user.username = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            user_data, created = UserData.objects.get_or_create(user=user)
            user_data.start_date = form.cleaned_data['start_date']
            user_data.end_date = form.cleaned_data['end_date']
            user_data.save()
        return super(UserFormView, self).form_valid(form)

    def get_success_url(self):
        return reverse("UserListView")