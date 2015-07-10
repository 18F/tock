from django.contrib import admin

from .models import Agency, Project, AccountingCode


class AgencyAdmin(admin.ModelAdmin):
    pass


class AccountingCodeAdmin(admin.ModelAdmin):
    pass


class ProjectAdmin(admin.ModelAdmin):
    pass


admin.site.register(Agency, AgencyAdmin)
admin.site.register(AccountingCode, AccountingCodeAdmin)
admin.site.register(Project, ProjectAdmin)
