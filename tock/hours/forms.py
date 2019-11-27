import json

import bleach
from django import forms
from django.db import connection, transaction
from django.db.models import Prefetch
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.utils.html import escapejs

from projects.models import AccountingCode, Project

from .models import ReportingPeriod, Timecard, TimecardObject


class ReportingPeriodForm(forms.ModelForm):
    """Form for creating new reporting periods"""

    class Meta:
        model = ReportingPeriod
        fields = ['start_date', 'end_date', 'min_working_hours', 'max_working_hours',]
        widgets = {
            'start_date': forms.TextInput(attrs={'class': "datepicker"}),
            'end_date': forms.TextInput(attrs={'class': "datepicker"})
        }


class ReportingPeriodImportForm(forms.Form):
    """Form for importing reporting period data"""

    reporting_period = forms.ModelChoiceField(
        queryset=ReportingPeriod.objects.all(), label="Reporting Period")
    line_items = forms.FileField(label="CSV of Objects in Reporting Period")


class TimecardForm(forms.ModelForm):

    class Meta:
        model = Timecard
        exclude = ['time_spent', 'reporting_period', 'user']


class SelectWithData(forms.widgets.Select):
    """
    Subclass of Django's select widget that allows disabling options.
    To disable an option, pass a dict instead of a string for its label,
    of the form: {'label': 'option label', 'disabled': True}
    """

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if isinstance(option['label'], dict):
            info = option['label']
            attrs = {}

            attrs['data-billable'] = "billable" if info.get('billable') else "non-billable"
            attrs['data-notes-displayed'] = "true" if info.get('notes_displayed') else "false"
            attrs['data-notes-required'] = "true" if info.get('notes_required') else "false"

            if info.get('alerts'):
                attrs['data-alerts'] = escapejs(json.dumps(info['alerts']))

            option['attrs'].update(attrs)
            option['label'] = info['label']
        return option


def choice_label_for_project(project):
    """
    Returns the label for a project as it should appear in an
    auto-completable list of choices.
    """

    return '%s - %s' % (project.id, project.name)


def projects_as_choices(queryset=None):
    """ Adds all of the projects in database to the TimeCardObjectForm project
    ChoiceField """

    accounting_codes = []

    if queryset is None:
        queryset = Project.objects.filter(active=True)

    prefetch_queryset = queryset.prefetch_related('alerts')
    prefetch = Prefetch('project_set', queryset=prefetch_queryset)

    for code in AccountingCode.objects.all().prefetch_related(prefetch, 'agency'):
        accounting_code = []
        projects = []

        for project in code.project_set.all():
            projects.append([
                project.id,
                {
                    'label': choice_label_for_project(project),
                    'billable': code.billable,
                    'notes_displayed': project.notes_displayed,
                    'notes_required': project.notes_required,
                    'alerts': [
                        {
                            'style': alert.full_style,
                            'text': alert.full_alert_text,
                            'url': alert.destination_url
                        }
                        for alert in project.alerts.all()
                    ],
                }
            ])

        accounting_code = [str(code), projects]
        accounting_codes.append(accounting_code)

    accounting_codes.append([
        '',
        [['', {
            'label': '',
            'billable': '',
            'notes_displayed': '',
            'notes_required': '',
            'alerts': [],
        }]]
    ])

    return accounting_codes


class TimecardObjectForm(forms.ModelForm):
    notes = forms.CharField(
        help_text='Please provide a snippet about how you spent your time.',
        required=False,
        widget=forms.Textarea(attrs={'class': 'entry-notes-text'})
    )
    project = forms.ChoiceField(
        widget=SelectWithData(),
        choices=projects_as_choices
    )

    hours_spent = forms.DecimalField(
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={
            'step': '0.50'
        })
    )


    class Meta:
        model = TimecardObject
        fields = ['project', 'hours_spent', 'notes']

    def clean_project(self):
        data = self.cleaned_data.get('project')

        try:
            data = Project.objects.get(id=data)
        except Project.DoesNotExist:
            raise forms.ValidationError('Invalid Project Selected')

        return data

    def clean_hours_spent(self):
        return self.cleaned_data.get('hours_spent') or 0

    def clean(self):
        if 'notes' in self.cleaned_data and 'project' in self.cleaned_data:
            self.cleaned_data['notes'] = bleach.clean(
                self.cleaned_data['notes'],
                tags=[],
                strip=True
            )
            if 'save_only' in self.data.keys():
                pass
            else:
                if self.cleaned_data['project'].notes_required and \
                    self.cleaned_data['notes'] == '':
                    self.add_error(
                        'notes',
                        forms.ValidationError(
                            'Please enter a snippet for your time tocked to '
                             + self.cleaned_data['project'].name
                        )
                    )
                elif not self.cleaned_data['project'].notes_displayed:
                    del self.cleaned_data['notes']

        return self.cleaned_data


class TimecardInlineFormSet(BaseInlineFormSet):
    """This FormSet is used for submissions of timecard entries."""

    def __init__(self, *args, **kwargs):
        super(TimecardInlineFormSet, self).__init__(*args, **kwargs)
        self.save_only = False
        self.aws_eligible = False

    def set_exact_working_hours(self, exact_working_hours):
        """ Set the number of hours employees should work """
        self.exact_working_hours = exact_working_hours

    def get_exact_working_hours(self):
        """ Return exact working hours required if it exists
        otherwise assumes 40 """
        return getattr(self, 'exact_working_hours', 40)

    def set_max_working_hours(self, max_working_hours):
        """ Set the maximum number of hours an employee may work in a period """
        self.max_working_hours = max_working_hours

    def get_max_working_hours(self):
        """ Return maximum number of hours an employee may work in a period
        if it exists, otherwise assumes 60 """
        return getattr(self, 'max_working_hours', 60)

    def set_min_working_hours(self, min_working_hours):
        """ Set the minimum number of hours an employee may work in a period """
        self.min_working_hours = min_working_hours

    def get_min_working_hours(self):
        """ Return minimum number of hours an employee may work in a period
        if it exists, otherwise assumes 40 """
        return getattr(self, 'min_working_hours', 40)

    def set_is_aws_eligible(self, aws_eligible):
        self.aws_eligible = aws_eligible

    def clean(self):
        super(TimecardInlineFormSet, self).clean()
        total_hrs = 0
        for form in self.forms:
            if form.cleaned_data:
                if form.cleaned_data.get('DELETE'):
                    continue
                if form.cleaned_data.get('hours_spent') is None:
                    raise forms.ValidationError(
                        'If you have a project listed, the number of hours '
                        'cannot be blank.'
                    )
                total_hrs += form.cleaned_data.get('hours_spent')
        if not self.save_only:
            for form in self.forms:
                try:
                    if form.cleaned_data['hours_spent'] == 0:
                        form.cleaned_data.update({'DELETE': True})
                except KeyError:
                    pass
            if len(self._errors[0].keys()) > 0:
                raise forms.ValidationError(
                    'Timecard not submitted because one or more of your '\
                    'entries has an error!'
                )
            if total_hrs > self.get_max_working_hours() and not self.aws_eligible:
                raise forms.ValidationError('You may not submit more than %s '
                    'hours for this period. To report additional hours'
                    ', please contact your supervisor.' % self.get_max_working_hours())

            if total_hrs < self.get_min_working_hours() and not self.aws_eligible:
                raise forms.ValidationError('You must report at least %s hours '
                    'for this period.' % self.get_min_working_hours())


        return getattr(self, 'cleaned_data', None)

    def save(self, commit=True):
        """
        Incoming TimeCardObjectForms may violate the unique by (project_id, timecard_id)
        constraint if users are swapping project_ids across TimeCardObjects which already
        exist in the database.

        From the user's perspective, the submitted timecard is valid and
        so long as the final state of the TimeCardObject table and the Timecard itself is valid
        we must accept the changes.

        To do that, we save the formset with constraints deferred so that
        they are checked at the end of the transaction.

        Additional details: https://github.com/18F/tock/issues/887
        """
        cur = connection.cursor()
        with transaction.atomic():
            cur.execute("SET CONSTRAINTS ALL DEFERRED")
            formset = super().save(commit=commit)
        return formset


def timecard_formset_factory(extra=1):
    return inlineformset_factory(
        Timecard,
        TimecardObject,
        extra=extra,
        form=TimecardObjectForm,
        formset=TimecardInlineFormSet
    )


TimecardFormSet = timecard_formset_factory()
