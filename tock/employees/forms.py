from django import forms
from django.forms import ModelForm

from employees.models import UserTravelRequest


class UserForm(forms.Form):
    first_name = forms.CharField(required=False, label="First Name")
    last_name = forms.CharField(required=False, label="Last Name")
    start_date = forms.DateField(
        required=False,
        label="Employment Start Date",
        widget=forms.TextInput(attrs={'class': "datepicker"}))
    end_date = forms.DateField(
        required=False, label="Employment End Date",
        widget=forms.TextInput(attrs={'class': "datepicker"}))
    current_employee = forms.BooleanField(
        required=False, label="Is this person a current OCSIT/18F employee?"
    )

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        current_employee = cleaned_data.get('current_employee')

        if end_date:
            if not start_date or (start_date >= end_date):
                raise forms.ValidationError(
                    "You must provide a start date before the user's end date."
                )


class UserTravelRequestForm(ModelForm):
    error_css_class = 'error'

    class Meta:
        model = UserTravelRequest
        fields = '__all__'
        widgets = {
            'departure_date': forms.TextInput(
                attrs={'class': 'datepicker'}
            ),
            'return_date': forms.TextInput(
                attrs={'class': 'datepicker'}
            ),
            'first_day_of_travel_work_date': forms.TextInput(
                attrs={'class': 'datepicker'}
            )
        }

    def clean(self):
        cleaned_data = super(UserTravelRequestForm, self).clean()

        departure_date = cleaned_data.get('departure_date')
        return_date = cleaned_data.get('return_date')
        first_day_of_travel_work_date = cleaned_data.get('first_day_of_travel_work_date')

        if not (departure_date and return_date and first_day_of_travel_work_date):
            raise forms.ValidationError(
                'You must provide each of dates requested below.'
            )

        if not ((departure_date <= first_day_of_travel_work_date) and (first_day_of_travel_work_date <= return_date)):
            raise forms.ValidationError(
                'Your departure, first day of travel work, and return dates must appear in the proper sequence.'
            )
