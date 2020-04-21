from django.contrib import admin

from .models import Organization, Unit


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'active',)
    list_filter = ('active',)
    search_fields = ('name',)


class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'org',)
    list_filter = ('org', 'active',)
    search_fields = ('name',)

admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Unit, UnitAdmin)
