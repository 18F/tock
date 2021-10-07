from decimal import Decimal
from math import isclose

from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import DecimalField, ModelForm
from django.forms.widgets import Select
from django.forms.models import BaseInlineFormSet
from employees.models import UserData

from .models import (HolidayPrefills, ReportingPeriod, Timecard, TimecardNote,
                     TimecardObject, TimecardPrefillData)


class ReportingPeriodListFilter(admin.SimpleListFilter):
    parameter_name = 'reporting_period'
    title = 'Reporting Period'

    def lookups(self, request, model_admin):
        data = ReportingPeriod.objects.distinct().values_list('start_date')

        return [(p[0], p[0]) for p in data]

    def queryset(self, request, queryset):
        return queryset


class DecimalChoiceWidget(Select):

    """A choice widget for decimal typed data.

    The Select widget when used with a form's TypedChoiceField that has an
    underlying `DecimalField` in the model is very sensitive to formatting because
    it uses string comparison (as is natural for a Select widget on a web page that
    deals in strings).

    This modifies the method in a `Select` widget where equality is checked so that
    it uses numerical equality. This should make it much better behaved with the
    numeric data type.
    """

    def optgroups(self, name, value, attrs=None):
        """Change the baseclass's method to use numerical comparison."""
        groups = []
        has_selected = False

        for index, (option_value, option_label) in enumerate(self.choices):
            if option_value is None:
                option_value = ''

            subgroup = []
            if isinstance(option_label, (list, tuple)):
                group_name = option_value
                subindex = 0
                choices = option_label
            else:
                group_name = None
                subindex = None
                choices = [(option_value, option_label)]
            groups.append((group_name, subgroup, index))

            for subvalue, sublabel in choices:
                selected = (
                    # instead of string comparison, use numerical comparison here
                    any(isclose(float(subvalue), float(v)) for v in value)
                    and (not has_selected or self.allow_multiple_selected)
                )
                has_selected |= selected
                subgroup.append(self.create_option(
                    name, subvalue, sublabel, selected, index,
                    subindex=subindex, attrs=attrs,
                ))
                if subindex is not None:
                    subindex += 1
        return groups


class TimecardObjectForm(ModelForm):

    class Meta:
        model = TimecardObject
        fields = "__all__"
        widgets = {"project_allocation": DecimalChoiceWidget}


class TimecardObjectFormset(BaseInlineFormSet):

    form = TimecardObjectForm

    def clean(self):
        """
        Check to ensure the proper number of hours are entered.
        """

        super(TimecardObjectFormset, self).clean()

        if any(self.errors):
            return

        hours = Decimal(0.0)
        weekly_billing_found = False
        aws_eligible = UserData.objects.get(
            user__id=self.instance.user_id).is_aws_eligible
        min_working_hours = self.instance.reporting_period.min_working_hours
        max_working_hours = self.instance.reporting_period.max_working_hours

        for unit in self.cleaned_data:
            try:
                if unit['hours_spent']:
                    hours = hours + unit['hours_spent']
                else:
                    if (unit['project_allocation'] and unit['project_allocation'] > 0):
                        weekly_billing_found = True
                        break
            except KeyError:
                pass

        if hours > max_working_hours and not aws_eligible:
            raise ValidationError(
                'You have entered more than %s hours' % max_working_hours
            )

        if hours < min_working_hours and not aws_eligible and not weekly_billing_found:
            raise ValidationError(
                'You have entered fewer than %s hours' % min_working_hours
            )


class ReportingPeriodAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'end_date', 'exact_working_hours', 'max_working_hours', 'min_working_hours', 'has_holiday_prefills', 'message_enabled',)
    list_editable = ('exact_working_hours', 'max_working_hours', 'min_working_hours', 'message_enabled',)
    filter_horizontal = ['holiday_prefills', ]


class TimecardObjectInline(admin.TabularInline):
    formset = TimecardObjectFormset
    form = TimecardObjectForm
    model = TimecardObject
    readonly_fields = [
        'grade',
        'revenue_profit_loss_account',
        'expense_profit_loss_account'
    ]


class TimecardAdminForm(ModelForm):
    billable_expectation = DecimalField(initial=settings.DEFAULT_BILLABLE_EXPECTATION)

    class Meta:
        model = Timecard
        fields = '__all__'


class TimecardAdmin(admin.ModelAdmin):
    inlines = (TimecardObjectInline,)
    list_display = ('user', 'reporting_period', 'billable_expectation', 'organization', 'submitted')
    list_editable = ('organization', 'billable_expectation')
    list_filter = ( 'user', ReportingPeriodListFilter, 'reporting_period')
    search_fields = ['user__username', 'reporting_period__start_date', 'reporting_period__end_date',]
    form = TimecardAdminForm


class TimecardNoteAdmin(admin.ModelAdmin):
    actions_on_bottom = True
    fields = ('title', 'body', 'style', 'enabled', 'display_period_start', 'display_period_end', 'position',)
    list_display = (
        'title',
        'enabled',
        'display_period_start',
        'display_period_end',
        'position',
        'style',
        'created',
        'modified',
    )
    list_editable = ('enabled', 'position', 'style',)
    list_filter = ('enabled', 'style',)
    readonly_fields = ('created', 'modified',)


class TimecardPrefillDataAdmin(admin.ModelAdmin):
    actions_on_bottom = True
    list_display = (
        'employee',
        'project',
        'hours',
        'is_active',
        'start_date',
        'end_date',
        'notes',
    )
    list_editable = ('hours',)
    list_filter = ('project__active',)
    search_fields = [
        'employee__user__username',
        'project__name',
        'project__mbnumber',
    ]


class TimecardPrefillDataInline(admin.TabularInline):
    model = TimecardPrefillData
    extra = 1


admin.site.register(HolidayPrefills)
admin.site.register(ReportingPeriod, ReportingPeriodAdmin)
admin.site.register(Timecard, TimecardAdmin)
admin.site.register(TimecardNote, TimecardNoteAdmin)
admin.site.register(TimecardPrefillData, TimecardPrefillDataAdmin)
