from django import forms


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
        required=False, label="Is this person a current 18F employee?"        
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
