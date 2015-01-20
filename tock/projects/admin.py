from django.contrib import admin

from .models import Agency, Project

class AgencyAdmin(admin.ModelAdmin):
    pass

class ProjectAdmin(admin.ModelAdmin):
    pass

admin.site.register(Agency, AgencyAdmin)
admin.site.register(Project, ProjectAdmin)
