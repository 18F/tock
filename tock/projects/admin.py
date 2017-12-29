from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django import forms

from .models import Agency, Project, ProfitLossAccount, ProjectAlert, AccountingCode
from hours.admin import TimecardPrefillDataInline

class AgencyAdmin(admin.ModelAdmin):
    search_fields = ['name',]


class AccountingCodeAdmin(admin.ModelAdmin):
    search_fields = ['agency__name', 'office',]

class ProfitLossAccountForm(forms.ModelForm):
    class Meta:
        model = ProfitLossAccount
        exclude = []
    def clean(self):
        start_date = self.cleaned_data.get('as_start_date', None)
        end_date = self.cleaned_data.get('as_end_date', None)

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError(
                    'Start date cannot occur after the end date.'
                )

        return self.cleaned_data

class ProfitLossAccountAdmin(admin.ModelAdmin):
    actions_on_bottom = True
    form = ProfitLossAccountForm
    list_display = ('name', 'accounting_string', 'as_start_date', 'as_end_date', 'account_type',)
    list_editable = ('accounting_string', 'account_type',)
    search_fields = ('name', 'accounting_string',)

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = []
    def clean(self):
        try:
            pl_info = self.cleaned_data['profit_loss_account']
            project_start = self.cleaned_data['start_date']

            if pl_info and \
            project_start and \
            (project_start < pl_info.as_start_date):
                raise forms.ValidationError(
                    'Profit/Loss accounting string will not be active '\
                    'until {}. Please select an profit/loss accounting '\
                    'string that is will be active on or before the start '\
                    'date of this project.'\
                    .format(
                        self.cleaned_data['profit_loss_account'].as_start_date
                    )
                )

            if pl_info and\
            (pl_info.account_type == 'Expense'):
                raise forms.ValidationError(
                    'You have assigned the {} profit/loss '\
                    'accounting information to {}. The accounting information '\
                    'type is {}, which is cannot be assigned to a '\
                    'project. Only accounting information that is of the '\
                    'Revenue type may be assigned to a project.'.format(
                        self.cleaned_data['profit_loss_account'],
                        self.cleaned_data['name'],
                        self.cleaned_data['profit_loss_account'].account_type
                    )
                )

        except KeyError:
            pass
        return self.cleaned_data

class ProjectAdmin(admin.ModelAdmin):
    form = ProjectForm
    inlines = (TimecardPrefillDataInline,)
    fields = [
        'name',
        'mbnumber',
        'accounting_code',
        'profit_loss_account',
        'project_lead',
        'start_date',
        'end_date',
        'active',
        'agreement_URL',
        'description',
        'alerts',
        'notes_required',
        'notes_displayed',
    ]
    list_display = (
        'name',
        'mbnumber',
        'accounting_code',
        'get_organization_name',
        'project_lead',
        'start_date',
        'end_date',
        'active',
        'notes_displayed',
        'notes_required',
    )
    list_filter = (
        'active',
        'notes_displayed',
        'notes_required',
        'organization__name'
    )
    search_fields = ('name', 'accounting_code__code', 'mbnumber',)

    def get_organization_name(self, obj):
        if obj.organization is not None:
            return obj.organization.name

        return '-'
    get_organization_name.short_description = 'Organization Name'

class ProjectAlertAdmin(admin.ModelAdmin):
    search_fields = ['title',]


admin.site.register(Agency, AgencyAdmin)
admin.site.register(AccountingCode, AccountingCodeAdmin)
admin.site.register(ProfitLossAccount, ProfitLossAccountAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectAlert, ProjectAlertAdmin)
