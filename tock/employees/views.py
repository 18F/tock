import datetime
import json

from django.contrib.auth.models import User
from django.db.models import Sum
from django.core.urlresolvers import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView
from django.shortcuts import get_object_or_404


from tock.utils import PermissionMixin, IsSuperUserOrSelf
from .utils import get_last_n_rp, get_rps_in_fy, calculate_utilization, utilization_by_range, get_fy_first_day

from .forms import UserForm
from .models import UserData

from hours.models import ReportingPeriod, TimecardObject


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
    start_tem = datetime.datetime.now()
    today = datetime.date.today()
    fy_first_day = get_fy_first_day(today)

    last_four_rp = get_last_n_rp(4, today)
    last_rp = last_four_rp[0]
    last_four_start_date = last_four_rp[3].start_date
    last_four_end_date = last_four_rp[0].end_date

    if last_four_end_date <= fy_first_day:
        earliest_date = last_four_start_date
    else:
        earliest_date = fy_first_day

    tos = TimecardObject.objects.filter(
        timecard__user__user_data__is_billable=True,
        timecard__submitted=True,
        timecard__reporting_period__start_date__gte=earliest_date.strftime(
            '%Y-%m-%d'
        )
    )

    def get_queryset(self):
        queryset = UserData.objects.filter(
            is_billable=True,
            current_employee=True
            )

        for userdata in queryset:
            start = datetime.datetime.now()
            user_tos = self.tos.filter(timecard__user=userdata.user)

            last_four_user_tos = user_tos.filter(
                timecard__reporting_period__start_date__gte=self.last_four_start_date.strftime('%Y-%m-%d')
            )
            last_four = calculate_utilization(last_four_user_tos)

            last_user_tos = last_four_user_tos.filter(
                timecard__reporting_period__pk=self.last_rp.pk
            )
            last = calculate_utilization(last_user_tos)

            fytd_user_tos = user_tos.filter(
                timecard__reporting_period__start_date__gte=self.fy_first_day
            )
            fytd = calculate_utilization(fytd_user_tos)

            userdata.last = last
            userdata.last_four = last_four
            userdata.fytd = fytd

        return queryset

    def get_context_data(self, **kwargs):
        context = super(GroupUtilizationView, self).get_context_data(**kwargs)

        context.update(
            {
                'unit_choices': UserData.objects.first().UNIT_CHOICES,
                'through_date': self.last_four_rp[0].end_date,
                'last_four_start_date': self.last_four_rp[len(self.last_four_rp)-1].start_date,
            }
        )

        end_tem = datetime.datetime.now()
        diff_tem = end_tem - self.start_tem
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
