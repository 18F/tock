import datetime

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.views.generic import ListView
from django.views.generic.edit import FormView

from tock.utils import PermissionMixin, IsSuperUserOrSelf

from .forms import UserForm
from .models import UserData


def parse_date(date):
    if date == 'NA':
        return None
    else:
        return datetime.datetime.strptime(date, '%m/%d/%Y')


class UserListView(ListView):
    template_name = 'employees/user_list.html'

    def get_queryset(self):
        return User.objects.select_related('user_data')

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        return context


class UserFormView(PermissionMixin, FormView):
    template_name = 'employees/user_form.html'
    form_class = UserForm
    permission_classes = (IsSuperUserOrSelf, )

    def get_context_data(self, **kwargs):
        current_user = User.objects.get(username=self.kwargs['username'])
        kwargs['name'] = UserData.objects.get(user=current_user.id).full_name()
        return super(UserFormView, self).get_context_data(**kwargs)

    def get_initial(self):
        initial = super(UserFormView, self).get_initial()
        user, created = User.objects.get_or_create(
            username=self.kwargs['username'])
        initial['first_name'] = user.first_name
        initial['last_name'] = user.last_name

        if hasattr(user, 'user_data'):
            initial['start_date'] = user.user_data.start_date
            initial['end_date'] = user.user_data.end_date
            initial['current_employee'] = user.user_data.current_employee

        return initial

    def form_valid(self, form):
        if form.is_valid():
            user, created = User.objects.get_or_create(
                username=self.kwargs['username'])
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            user_data, created = UserData.objects.get_or_create(user=user)
            user_data.start_date = form.cleaned_data['start_date']
            user_data.end_date = form.cleaned_data['end_date']
            user_data.current_employee = form.cleaned_data['current_employee']
            user_data.save()
        return super(UserFormView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'employees:UserListView',
            current_app=self.request.resolver_match.namespace,
        )
