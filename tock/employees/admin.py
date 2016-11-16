from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django import forms

from .models import UserData, EmployeeGrade

class UserDataForm(forms.ModelForm):
    model = UserData
    def clean(self):
        if self.cleaned_data['profit_loss_account'].account_type == 'Revenue':
            raise forms.ValidationError('You have assigned the {} profit/loss '\
                'accounting information to {}. The accounting information '\
                'type is {}, which is cannot be assigned to an '\
                'employee. Only accounting information of the Expense type '\
                'may be assigned to an employee.'.format(
                    self.cleaned_data['profit_loss_account'],
                    self.cleaned_data['user'],
                    self.cleaned_data['profit_loss_account'].account_type
                )
            )

        if self.cleaned_data['profit_loss_account'].as_start_date > \
            self.cleaned_data['start_date']:
            raise forms.ValidationError('The profit/loss accounting '\
                'information you have selected, {}, has a start date that is '\
                'after the start date of {}. Please select profit/loss '\
                'accounting information with a start date that occurs on or '\
                'before {}.'.format(
                    self.cleaned_data['profit_loss_account'],
                    self.cleaned_data['user'],
                    self.cleaned_data['start_date']
                )
            )
        if self.cleaned_data['profit_loss_account'].as_end_date < \
            self.cleaned_data['start_date']:
                raise forms.ValidationError('The profit/loss accounting' \
                'information you have selected, {}, has an end date that is '\
                'before the start date of {}. Please select a profit/loss '\
                'accounting information with an end date that occurs '\
                'after {}'.format(
                    self.cleaned_data['profit_loss_account'],
                    self.cleaned_data['user'],
                    self.cleaned_data['start_date']
                ))
        return self.cleaned_data

class UserDataAdmin(admin.ModelAdmin):
    form = UserDataForm
    list_display = ('user',)
    search_fields = ('user__username',)

class EmployeeGradeAdmin(admin.ModelAdmin):
    search_fields = ('employee__username',)

admin.site.register(UserData, UserDataAdmin)
admin.site.register(EmployeeGrade, EmployeeGradeAdmin)
