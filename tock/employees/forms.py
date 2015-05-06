from django import forms
from django.forms.models import BaseInlineFormSet
from django.contrib.auth.models import User
from django.forms.models import modelformset_factory

from .models import UserData

class UserForm(forms.Form):
	email = forms.EmailField(required=True, label="Email Address")
	first_name = forms.CharField(required=False, label="First Name")
	last_name = forms.CharField(required=False, label="Last Name")
	start_date = forms.DateField(required=False, label="Employment Start Date")
	end_date = forms.DateField(required=False, label="Employment End Date")
