import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormView
from rest_framework.permissions import IsAuthenticated
from tock.utils import IsSuperUserOrSelf, PermissionMixin

from .forms import UserForm
from .models import UserData
from utilization.employee import user_billing_context


def parse_date(date):
    if date == 'NA':
        return None
    else:
        return datetime.datetime.strptime(date, '%m/%d/%Y')


class UserListView(PermissionMixin, ListView):
    template_name = 'employees/user_list.html'
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return User.objects.filter(is_active=True).select_related('user_data')


class UserDetailView(PermissionMixin, DetailView):
    template_name = 'employees/user_detail.html'
    permission_classes = (IsAuthenticated, )

    def get_object(self, **kwargs):
        kwargs['username'] = self.kwargs['username']
        target_user = UserData.objects.get(
            user__username=self.kwargs['username'])
        return target_user

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        user = self.get_object().user
        context.update(user_billing_context(user))
        return _add_recent_tock_table(user, context)


class UserFormView(PermissionMixin, FormView):
    template_name = 'employees/user_form.html'
    form_class = UserForm
    permission_classes = (IsSuperUserOrSelf, )

    def get_context_data(self, **kwargs):
        kwargs['username'] = self.kwargs['username']
        user = User.objects.get(username=kwargs['username'])
        context = super(UserFormView, self).get_context_data(**kwargs)
        context.update(user_billing_context(user))
        return _add_recent_tock_table(user, context)

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

def _add_recent_tock_table(user, context):
    """
    For a given user, return an updated context including
    the data necessary to render a table of projects and hours billed
    for the last `settings.RECENT_TOCKS_TO_REPORT` time periods
    """
    recent_tocks = user.timecards.order_by('-reporting_period__start_date')[:settings.RECENT_TOCKS_TO_REPORT]
    recent_tocks = list(reversed(recent_tocks))
    billing_table = {}
    for n, timecard in enumerate(recent_tocks):
        for tco in timecard.timecardobjects.all().select_related('project'):
            project_billing = billing_table.setdefault(tco.project, [0] * len(recent_tocks))
            project_billing[n] = tco.hours_spent
    context['recent_billing_table'] = billing_table
    context['recent_timecards'] = recent_tocks
    return context
