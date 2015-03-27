from django import forms
from django.forms.models import BaseInlineFormSet
from django.forms.models import inlineformset_factory

from .models import Timecard, TimecardObject

class TimecardForm(forms.ModelForm):
    class Meta:
        model = Timecard
        exclude = ['time_spent', 'reporting_period', 'user']

class TimecardObjectForm(forms.ModelForm):
    class Meta:
        model = TimecardObject
        fields = ['project', 'time_percentage']

class TimecardInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super(TimecardInlineFormSet, self).clean()

        total_number_of_hours = 0
        for form in self.forms:
            if form.cleaned_data:
                total_number_of_hours += form.cleaned_data['time_percentage']

        if total_number_of_hours != 100:
            raise forms.ValidationError('You must report exactly 100%. \
                        You reported {:.0f}%.'.format(total_number_of_hours))

        return self.cleaned_data

TimecardFormSet = inlineformset_factory(Timecard, TimecardObject, extra=1, formset=TimecardInlineFormSet)