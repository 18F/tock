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
    """This FormSet is used for submissions of timecard entries. Right now,
    it only works for initial entries and not for updates :/"""
    def clean(self):
        super(TimecardInlineFormSet, self).clean()

        # We set the total number of hours to zero, then iterate through each
        # individal formset submission
        total_number_of_hours = 0
        for form in self.forms:
            if form.cleaned_data:
                # Easy way of telling if we have the right data
                if form.cleaned_data.get('time_percentage') == None:
                    # Don't allow submissions that specify a project but not a
                    # percentage of time
                    raise forms.ValidationError('If you have a project listed, \
                        the Time Percentage cannot be blank')
                # Add the time percentage to the total number of hours
                total_number_of_hours += form.cleaned_data.get('time_percentage')

        if total_number_of_hours != 100:
            # If you have more or less than 100, then you are not counting time
            # right.
            raise forms.ValidationError('You must report exactly 100%.')

        return self.cleaned_data

TimecardFormSet = inlineformset_factory(Timecard, TimecardObject, 
    extra=1, formset=TimecardInlineFormSet)