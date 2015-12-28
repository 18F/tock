from django import forms
from django.forms.models import BaseInlineFormSet
from django.forms.models import inlineformset_factory
from django.utils.encoding import force_text
from django.utils.html import escape, conditional_escape
from django.db.models import Prefetch

from .models import Timecard, TimecardObject, ReportingPeriod
from projects.models import AccountingCode, Project


class ReportingPeriodForm(forms.ModelForm):

    class Meta:
        model = ReportingPeriod
        fields = ['start_date', 'end_date', 'working_hours', 'message']
        widgets = {
            'start_date': forms.TextInput(attrs={'class': "datepicker"}),
            'end_date': forms.TextInput(attrs={'class': "datepicker"})
        }


class ReportingPeriodImportForm(forms.Form):
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

    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_text(option_value)
        if (option_value in selected_choices):
            selected_html = u' selected="selected"'
        else:
            selected_html = ''
        billable_html = ''
        if isinstance(option_label, dict):
            if dict.get(option_label, 'billable'):
                billable_html = ' data-billable="billable"'
            else:
                billable_html = ' data-billable="non-billable"'
            option_label = option_label['label']
        return '<option value="%s"%s%s>%s</option>' % (
            escape(option_value), selected_html, billable_html,
            conditional_escape(force_text(option_label)))


def projects_as_choices():
    """ Adds all of the projects in database to the TimeCardObjectForm project
    ChoiceField """
    accounting_codes = []
    prefetch = Prefetch('project_set', queryset=Project.objects.filter(active=True))
    for code in AccountingCode.objects.all().prefetch_related(prefetch, 'agency'):
        accounting_code = []
        projects = []
        for project in code.project_set.all():
            projects.append([
                project.id,
                {
                    'label': project.name,
                    'billable': code.billable
                }
            ])
        accounting_code = [str(code), projects]
        accounting_codes.append(accounting_code)
    accounting_codes.append(
        ['', [['', {'label': '', 'billable': ''}]]])
    return accounting_codes


class TimecardObjectForm(forms.ModelForm):
    project = forms.ChoiceField(
        widget=SelectWithData(), choices=projects_as_choices)

    class Meta:
        model = TimecardObject
        fields = ['project', 'hours_spent']

    def clean_project(self):
        data = self.cleaned_data.get('project')
        try:
            data = Project.objects.get(id=data)
        except Project.DoesNotExist:
            raise forms.ValidationError('Invalid Project Selected')
        return data


class TimecardInlineFormSet(BaseInlineFormSet):
    """This FormSet is used for submissions of timecard entries. Right now,
      it only works for initial entries and not for updates :/"""

    def set_working_hours(self, working_hours):
        """ Set the number of hours employees should work """
        self.working_hours = working_hours

    def get_working_hours(self):
        """ Return working hours if it exists otherwise assumes 40 """
        return getattr(self, 'working_hours', 40)

    def clean(self):
        super(TimecardInlineFormSet, self).clean()
        total_number_of_hours = 0
        for form in self.forms:
            if form.cleaned_data:
                if not form.cleaned_data.get('hours_spent'):
                    raise forms.ValidationError(
                        'If you have a project listed, the number of hours '
                        'cannot be blank'
                    )
                total_number_of_hours += form.cleaned_data.get('hours_spent')
        if total_number_of_hours != self.get_working_hours():
            raise forms.ValidationError(
                'You must report exactly %s hours.' % self.get_working_hours())
        return getattr(self, 'cleaned_data', None)


TimecardFormSet = inlineformset_factory(Timecard, TimecardObject,
                                        extra=1, form=TimecardObjectForm,
                                        formset=TimecardInlineFormSet)
