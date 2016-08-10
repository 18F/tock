from django import forms
from django.contrib import admin
from .models import Agency, Project, ProjectAlert, AccountingCode, EngagementInformation


class AgencyAdmin(admin.ModelAdmin):
    search_fields = ['agency_name',]


class AccountingCodeAdmin(admin.ModelAdmin):
    search_fields = []
    readonly_fields = ['egmt_agency', 'egmt_office', 'engagement_uuid']
    fields = [
        'engagement',
        'egmt_agency',
        'egmt_office',
        'engagement_uuid',
        'billable',
        'flat_rate',
        'pp_start_date',
        'pp_end_date',
        'amount',
        'notes',
        ]
"""
class AccountingCodeForm(forms.ModelForm):
    class Meta:
        model = AccountingCode

    def clean(self):
        egmt_start_date = self.engagement.agmt_start_date
        egmt_end_date = self.engagement.agmt_end_date
        if self.pp_start_date < egmt_start_date:
            raise forms.ValidationError('Order start date occurs before'
                'engagement start date.')
        return self.clean
"""


class ProjectAdmin(admin.ModelAdmin):
    search_fields = ['name',]
    readonly_fields = ['auto_deactivate_date','active','aggregate_hours_logged',
        'engagement',]
    fields = [
        'accounting_code',
        'active',
        'engagement',
        'name',
        'mbnumber',
        'description',
        'start_date',
        'end_date',
        'auto_deactivate_days',
        'auto_deactivate_date',
        'max_hours_restriction',
        'max_hours',
        'aggregate_hours_logged',
        'notes_required',
        'notes_displayed',
        'alerts',
        ]

class ProjectAlertAdmin(admin.ModelAdmin):
    search_fields = ['title',]

class EngagementInformationAdmin(admin.ModelAdmin):
    readonly_fields = ('engagement_uuid',)
    fields = (
        'client',
        'engagement_uuid',
        'iaa_number',
        'agmt_start_date',
        'agmt_end_date',
    )


admin.site.register(Agency, AgencyAdmin)
admin.site.register(AccountingCode, AccountingCodeAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectAlert, ProjectAlertAdmin)
admin.site.register(EngagementInformation, EngagementInformationAdmin)
