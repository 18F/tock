from decimal import Decimal

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import ReportingPeriod, Timecard, TimecardObject

class ReportingPeriodListFilter(admin.SimpleListFilter):
    title = 'Reporting Period'
    parameter_name = 'reporting_period'

    def lookups(self, request, model_admin):
        reportingperiods = set([p.start_date for p in ReportingPeriod.objects.all()])
        return [(p, p) for p in reportingperiods]

    def queryset(self, request, queryset):
        return queryset

class TimecardObjectFormset(BaseInlineFormSet):
    def clean(self):
        '''Check to ensure the proper number of hours are entered'''
        super(TimecardObjectFormset, self).clean()

        if any(self.errors):
            return

        percentage = Decimal(0.0)

        for unit in self.cleaned_data:
            try:
                percentage = percentage + unit["time_percentage"]
            except KeyError:
                pass

        if percentage > 100:
            raise ValidationError('You have entered more than 100%')

        if percentage < 100:
            raise ValidationError('You have entered less than 100%')


class ReportingPeriodAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'end_date')

class TimecardObjectInline(admin.TabularInline):
    model = TimecardObject
    formset = TimecardObjectFormset

class TimecardAdmin(admin.ModelAdmin):
    list_display = ('user', 'reporting_period',)
    list_filter = (ReportingPeriodListFilter, 'reporting_period')
    inlines = (TimecardObjectInline,)

admin.site.register(ReportingPeriod, ReportingPeriodAdmin)
admin.site.register(Timecard, TimecardAdmin)