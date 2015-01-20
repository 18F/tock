from django.contrib import admin

from .models import Week

class WeekAdmin(admin.ModelAdmin):
    pass

admin.site.register(Week, WeekAdmin)