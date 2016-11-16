from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django import forms

from .models import Agency, Project, ProfitLossAccount, ProjectAlert, AccountingCode


class AgencyAdmin(admin.ModelAdmin):
    search_fields = ['name',]


class AccountingCodeAdmin(admin.ModelAdmin):
    search_fields = ['agency__name', 'office',]

class ProfitLossAccountForm(forms.ModelForm):
    model = ProfitLossAccount
    def clean(self):

        if self.cleaned_data.get(
            'as_start_date'
        ) > self.cleaned_data.get(
            'as_end_date'
        ):
            raise forms.ValidationError(
                'Start date cannot occur before the end date.'
            )
        return self.cleaned_data

class ProfitLossAccountAdmin(admin.ModelAdmin):
    form = ProfitLossAccountForm
    search_fields = ['name',]
    readonly_fields = ['as_active']

class ProjectAdmin(admin.ModelAdmin):
    search_fields = ['name',]

class ProjectAlertAdmin(admin.ModelAdmin):
    search_fields = ['title',]


admin.site.register(Agency, AgencyAdmin)
admin.site.register(AccountingCode, AccountingCodeAdmin)
admin.site.register(ProfitLossAccount, ProfitLossAccountAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectAlert, ProjectAlertAdmin)
