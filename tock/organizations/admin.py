from django.contrib import admin

from .models import Organization


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'active',)
    list_filter = ('active',)
    search_fields = ('name',)

admin.site.register(Organization, OrganizationAdmin)
