from decimal import Decimal

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import ReportingPeriod, Timecard, TimecardObject


class ReportingPeriodListFilter(admin.SimpleListFilter):
    parameter_name = 'reporting_period'
    title = 'Reporting Period'

    def lookups(self, request, model_admin):
        data = ReportingPeriod.objects.distinct().values_list('start_date')

        return [(p[0], p[0]) for p in data]

    def queryset(self, request, queryset):
        return queryset



class TimecardObjectFormset(BaseInlineFormSet):
    def clean(self):
        """
        Check to ensure the proper number of hours are entered.
        """

        super(TimecardObjectFormset, self).clean()

        if any(self.errors):
            return

        hours = Decimal(0.0)
        superuser_hours = Decimal(60.0)
        zero_to_60 = False
        working_hours = self.instance.reporting_period.working_hours

        for unit in self.cleaned_data:
            try:
                hours = hours + unit['hours_spent']
                zero_to_60 = unit['timecard'].zero_to_60
            except KeyError:
                pass

        if hours > working_hours and not zero_to_60:
            raise ValidationError(
                'You have entered more than %s hours' % working_hours
            )

        if hours > superuser_hours and zero_to_60:
            raise ValidationError(
                'You have entered more than %s hours' % superuser_hours
            )

        if hours < working_hours and not zero_to_60:
            raise ValidationError(
                'You have entered fewer than %s hours' % working_hours
            )


class ReportingPeriodAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'end_date',)
    filter_horizontal = ('users',)


class TimecardObjectInline(admin.TabularInline):
    formset = TimecardObjectFormset
    model = TimecardObject


class TimecardAdmin(admin.ModelAdmin):
    inlines = (TimecardObjectInline,)
    list_display = ('user', 'reporting_period',)
    list_filter = (ReportingPeriodListFilter, 'reporting_period',)
    search_fields = ['user__username', 'reporting_period__start_date', 'reporting_period__end_date',]


admin.site.register(ReportingPeriod, ReportingPeriodAdmin)
admin.site.register(Timecard, TimecardAdmin)
