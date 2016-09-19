from django.contrib import admin

from .models import Agency, Project, ProjectAlert, AccountingCode


class AgencyAdmin(admin.ModelAdmin):
    search_fields = ['name',]


class AccountingCodeAdmin(admin.ModelAdmin):
    search_fields = ['agency__name', 'office',]


class ProjectAdmin(admin.ModelAdmin):
    search_fields = ['name',]
    readonly_fields = ('auto_deactivate_date',)
    fields = (
        'name',
        'mbnumber',
        'accounting_code',
        'description',
        'start_date',
        'end_date',
        'active',
        'auto_deactivate_days',
        'auto_deactivate_date',
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
