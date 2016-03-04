import datetime
from string import Template

from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.loader import render_to_string
from django.views.generic import ListView
from django.views.generic.edit import FormView

from .forms import UserForm, UserTravelRequestForm
from .models import UserData
from tock.utils import PermissionMixin, IsSuperUserOrSelf


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


class UserTravelRequestFormView(PermissionMixin, FormView):
    form_class = UserTravelRequestForm
    template_name = 'employees/user_travel_form.html'
    permission_classes = (IsSuperUserOrSelf,)

    def get_context_data(self, **kwargs):
        kwargs['username'] = self.kwargs['username']
        return super(UserTravelRequestFormView, self).get_context_data(**kwargs)

    def get_initial(self):
        initial = super(UserTravelRequestFormView, self).get_initial()
        user, created = User.objects.get_or_create(
            username=self.kwargs['username']
        )
        initial['requestor_email'] = user.email
        initial['requestor_name'] = user.first_name + ' ' + user.last_name

        return initial

    def form_valid(self, form):
        if form.is_valid():
            subject = Template(
                '${billability} - ${tock_project_name} - #${tock_project_id} -- ${departure_date} - ${return_date}'
            ).substitute(
                billability=form.cleaned_data['billability'],
                tock_project_name=form.cleaned_data['tock_project_name'],
                tock_project_id=form.cleaned_data['tock_project_id'],
                departure_date=form.cleaned_data['departure_date'],
                return_date=form.cleaned_data['return_date'],
            )
            message_context = Context({
                'home_location': form.cleaned_data['home_location'],
                'work_location': form.cleaned_data['work_location'],
                'departure_date': form.cleaned_data['departure_date'],
                'return_date': form.cleaned_data['return_date'],
                'work_to_be_done': form.cleaned_data['work_to_be_done'],
                'first_day_of_travel_work_date': form.cleaned_data['first_day_of_travel_work_date'],
                'requestor_name': form.cleaned_data['requestor_name']
            })
            message_plain = render_to_string('employees/user_travel_form_email.txt', message_context)
            message_html = render_to_string('employees/user_travel_form_email.html', message_context)

            email = EmailMultiAlternatives(
                to=[
                    form.cleaned_data['client_email']
                ],
                subject=subject,
                body=message_plain,
                reply_to=[
                    form.cleaned_data['requestor_email'],
                    '18fTravelAuths@gsa.gov'
                ]
            )
            email.attach_alternative(message_html, 'text/html')
            email.send()

        return super(UserTravelRequestFormView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'employees:UserListView',
            current_app=self.request.resolver_match.namespace
        )
