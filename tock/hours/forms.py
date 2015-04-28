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
    fields = ['project', 'hours_spent']


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
                                        extra=1,
                                        formset=TimecardInlineFormSet)
