from django import forms
from django.forms.models import BaseInlineFormSet
from django.forms.models import inlineformset_factory
from django.utils.encoding import force_text
from django.utils.html import escape, conditional_escape

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
    accounting_codes = []
    for code in AccountingCode.objects.all():
        accounting_code = []
        projects = []
        for project in code.project_set.all():
            projects.append([project.id, {'label': project.name,
                                          'billable': project.accounting_code.billable}])

        accounting_code = [str(code), projects]
        accounting_codes.append(accounting_code)
    accounting_codes.append(['', [['', {'label': '',
                                          'billable': ''}]]])
    return accounting_codes


class TimecardObjectForm(forms.ModelForm):

    project = forms.ChoiceField(
        choices=projects_as_choices(), widget=SelectWithData())

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

    def clean(self):
        super(TimecardInlineFormSet, self).clean()

        # We set the total number of hours to zero, then iterate through each
        # individal formset submission
        total_number_of_hours = 0
        for form in self.forms:
            # print(form)
            if form.cleaned_data:
                # Easy way of telling if we have the right data
                if form.cleaned_data.get('hours_spent') == None:
                    # Don't allow submissions that specify a project but not a
                    # amount of time
                    raise forms.ValidationError('If you have a project listed, \
                        the number of hours cannot be blank')
                # Add the time to the total number of hours
                total_number_of_hours += form.cleaned_data.get('hours_spent')

        if total_number_of_hours != 40:
            # If you have more or less than 40, then you are not counting time
            # right.
            raise forms.ValidationError('You must report exactly 40 hours.')

        return self.cleaned_data


TimecardFormSet = inlineformset_factory(Timecard, TimecardObject,
                                        extra=1, form=TimecardObjectForm,
                                        formset=TimecardInlineFormSet)
