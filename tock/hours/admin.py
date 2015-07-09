from decimal import Decimal

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import ReportingPeriod, Timecard, TimecardObject


class ReportingPeriodListFilter(admin.SimpleListFilter):
    title = 'Reporting Period'
    parameter_name = 'reporting_period'

    def lookups(self, request, model_admin):
        data = ReportingPeriod.objects.distinct().values_list('start_date')
        return [(p[0], p[0]) for p in data]

    def queryset(self, request, queryset):
        return queryset


class TimecardObjectFormset(BaseInlineFormSet):

    def clean(self):
        '''Check to ensure the proper number of hours are entered'''
        super(TimecardObjectFormset, self).clean()

        if any(self.errors):
            return

        hours = Decimal(0.0)
        for unit in self.cleaned_data:
            try:
                hours = hours + unit["hours_spent"]
            except KeyError:
                pass
        if hours > 40:
            raise ValidationError('You have entered more than 40 hours')

        if hours < 40:
            raise ValidationError('You have entered fewer than 40 hours')


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
