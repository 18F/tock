from django.contrib import admin

from .models import Agency, Project, ProjectAlert, AccountingCode


class AgencyAdmin(admin.ModelAdmin):
    search_fields = ['name',]


class AccountingCodeAdmin(admin.ModelAdmin):
    search_fields = ['agency__name', 'office',]


class ProjectAdmin(admin.ModelAdmin):
    search_fields = ['name',]
    readonly_fields = ['all_hours_logged',]
    fields = [
        'name',
        'description',
        'accounting_code',
        'active',
        'mbnumber',
        'end_date',
        'start_date',
        'max_hours_restriction',
        'max_hours',
        'all_hours_logged',
        'notes_displayed',
        'notes_required',
        'alerts',
        ]

class ProjectAlertAdmin(admin.ModelAdmin):
    search_fields = ['title',]


admin.site.register(Agency, AgencyAdmin)
admin.site.register(AccountingCode, AccountingCodeAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectAlert, ProjectAlertAdmin)
