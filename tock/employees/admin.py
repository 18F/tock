from django.contrib import admin
from django import forms

from .models import UserData, EmployeeGrade
from hours.admin import TimecardPrefillDataInline


class UserDataForm(forms.ModelForm):
    class Meta:
        model = UserData
        exclude = []
    def clean(self):
        try:
            pl_info = self.cleaned_data['profit_loss_account']
            if pl_info and \
            (pl_info.account_type == 'Revenue'):
                raise forms.ValidationError('You have assigned the {} '\
                    'profit/loss accounting information to {}. The accounting '\
                    'information type is {}, which is cannot be assigned to '\
                    'an employee. Only accounting information of the Expense '\
                    'type may be assigned to an employee.'.format(
                        pl_info,
                        self.cleaned_data['user'],
                        pl_info.account_type
                    )
                )

            if pl_info and \
            (pl_info.as_end_date < self.cleaned_data['start_date']):
                raise forms.ValidationError('The profit/loss accounting' \
                    'information you have selected, {}, has an end date that '\
                    'is before the start date of {}. Please select a '\
                    'profit/loss accounting information with an end date that '\
                    'occurs after {}'.format(
                        pl_info,
                        self.cleaned_data['user'],
                        self.cleaned_data['start_date']
                    )
                )
        except KeyError:
            pass
        return self.cleaned_data

class UserDataAdmin(admin.ModelAdmin):
    form = UserDataForm
    inlines = (TimecardPrefillDataInline,)
    list_display = (
        'user',
        'start_date',
        'end_date',
        'get_organization_name',
        'unit_info',
        'current_employee',
        'is_18f_employee',
        'is_billable',
        'is_aws_eligible',
    )
    list_filter = (
        'current_employee',
        'is_18f_employee',
        'is_billable',
        'is_aws_eligible',
        'organization__name',
    )
    search_fields = ('user__username',)

    def unit_info(self, obj):
        """
        Because historically unit was not a required field,
        don't follow the relationship to `unit.name` or we'll break the admin.
        Instead, let Django resolve the object `str` if it doesn't exist.
        """
        return obj.unit
    unit_info.short_description = 'Unit'

    def get_organization_name(self, obj):
        if obj.organization is not None:
            return obj.organization.name

        return '-'
    get_organization_name.short_description = 'Organization Name'


class EmployeeGradeAdmin(admin.ModelAdmin):
    search_fields = ('employee__username',)

admin.site.register(UserData, UserDataAdmin)
admin.site.register(EmployeeGrade, EmployeeGradeAdmin)
