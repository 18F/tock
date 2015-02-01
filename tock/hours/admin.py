from django.contrib import admin

from .models import Week, Timecard, TimecardObject

class WeekAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'end_date')

class TimecardObjectInline(admin.TabularInline):
    model = TimecardObject
    extra = 5

class TimecardAdmin(admin.ModelAdmin):
    inlines = (TimecardObjectInline,)

admin.site.register(Week, WeekAdmin)
admin.site.register(Timecard, TimecardAdmin)