from django.contrib import admin

from .models import Agency, Project, ProjectAlert, AccountingCode


class AgencyAdmin(admin.ModelAdmin):
    search_fields = ['name',]


class AccountingCodeAdmin(admin.ModelAdmin):
    search_fields = ['agency__name', 'office',]


class ProjectAdmin(admin.ModelAdmin):
    search_fields = ['name',]
    readonly_fields = ('auto_deactivate_date','active','aggregate_hours_logged',)
    fields = (
        'name',
        'active',
        'mbnumber',
        'accounting_code',
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
        )
        
class ProjectAlertAdmin(admin.ModelAdmin):
    search_fields = ['title',]


admin.site.register(Agency, AgencyAdmin)
admin.site.register(AccountingCode, AccountingCodeAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectAlert, ProjectAlertAdmin)
