import datetime

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView
from django.shortcuts import get_object_or_404


from tock.utils import PermissionMixin, IsSuperUserOrSelf
from .utils import calculate_utilization, utilization_by_rp

from .forms import UserForm
from .models import UserData

from hours.models import ReportingPeriod


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

class GroupUtilizationView(ListView):
    template_name = 'employees/group_utilization.html'

    def get_queryset(self):
        queryset = UserData.objects.filter(
            is_billable=True,
            current_employee=True
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super(GroupUtilizationView, self).get_context_data(**kwargs)
        queryset = self.get_queryset()

        def get_last_n_rp(n, date):
            rp_queryset = ReportingPeriod.objects.filter(
                end_date__lte=date).order_by('-start_date')
            return rp_queryset[:n]

        def get_weeks_in_fy(date):
            if date.month <= 9:
                year = date.year - datetime.timedelta(weeks=52)
            else:
                year = date.year
            target = datetime.date(year, 10, 1)
            n = len(ReportingPeriod.objects.filter(start_date__gt=target))
            return n

        today = datetime.date.today()
        last_rp = get_last_n_rp(1, today)
        last_four_rp = get_last_n_rp(4, today)
        last_eight_rp = get_last_n_rp(8, today)
        fytd_rp = get_last_n_rp(get_weeks_in_fy(today), today)

        context.update(
            {
                'unit_choices': queryset[0].UNIT_CHOICES,
                'last_start_date': last_rp[0].start_date,
                'last_end_date': last_rp[0].end_date,
                'last_four_start_date': last_four_rp[len(last_four_rp)-1].start_date,
                'last_four_end_date': last_four_rp[0].end_date,
                'last_eight_start_date': last_eight_rp[len(last_eight_rp)-1].start_date,
                'last_eight_end_date': last_eight_rp[0].end_date,
                'fytd_end_date': fytd_rp[0].end_date,
                'last': '',
                'last_four': '',
                'last_eight': '',
                'fytd': ''
            }
        )

        return context

class UserUtilizationView(DetailView):
    template_name = 'employees/user_utilization.html'

    def get_user(self):
        pass

class UserDetailView(DetailView):
    template_name = 'employees/user_detail.html'

    def get_object(self, **kwargs):
        kwargs['username'] = self.kwargs['username']
        target_user = UserData.objects.get(
            user__username=self.kwargs['username'])
        return target_user

class UserFormView(PermissionMixin, FormView):
    template_name = 'employees/user_form.html'
    form_class = UserForm
    permission_classes = (IsSuperUserOrSelf, )

    def get_context_data(self, **kwargs):
        kwargs['username'] = self.kwargs['username']
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
