import datetime

from .utils import ValidateOnSaveMixin
from projects.models import Project, ProfitLossAccount

from django.contrib.auth.models import User
from employees.models import EmployeeGrade
from django.core.validators import MaxValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, Max


class HolidayPrefills(models.Model):
    """For use with ReportingPeriods to prefill timecards."""
    project = models.ForeignKey(Project)
    hours_per_period = models.PositiveSmallIntegerField(default=8)

    def __str__(self):
        return '{} ({} hrs.)'.format(self.project.name, self.hours_per_period)

    class Meta:
        verbose_name = 'Holiday Prefills'
        verbose_name_plural = 'Holiday Prefills'
        unique_together = ['project', 'hours_per_period']
        ordering = ['project__name']

class Targets(models.Model):
    name = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )
    start_date = models.DateField(
        unique=True
    )
    end_date = models.DateField(
        unique=True
    )
    hours_target_cr = models.PositiveIntegerField(
        default=0,
        verbose_name='Hours target for cost recovery'
    )
    hours_target_plan = models.PositiveIntegerField(
        default=0,
        verbose_name='Hours target for financial plan'
    )
    revenue_target_cr = models.PositiveIntegerField(
        default=0,
        verbose_name='Revenue target for financial plan'
    )
    revenue_target_plan = models.PositiveIntegerField(
        default=0,
        verbose_name='Revenue target for financial plan',
    )
    periods = models.PositiveSmallIntegerField(
        default=52,
    )
    labor_rate = models.PositiveSmallIntegerField(
        default=1
    )

    def fiscal_year(self):
        return ReportingPeriod.get_fiscal_year(self)

    def __str__(self):
        return '{} (FY{})'.format(self.name, self.fiscal_year())

    class Meta:
        unique_together = ("start_date", "end_date")
        verbose_name = 'Target'
        verbose_name_plural = 'Targets'

class ReportingPeriod(ValidateOnSaveMixin, models.Model):
    USWDS_ALERT_SUCCESS = 'success'
    USWDS_ALERT_WARNING = 'warning'
    USWDS_ALERT_ERROR = 'error'
    USWDS_ALERT_INFO = 'info'

    USWDS_ALERT_CHOICES = (
        (USWDS_ALERT_INFO, 'Blue (Info)'),
        (USWDS_ALERT_SUCCESS, 'Green (Success)',),
        (USWDS_ALERT_WARNING, 'Yellow (Warning)'),
        (USWDS_ALERT_ERROR, 'Red (Error)'),
    )

    """Reporting period model details"""
    start_date = models.DateField(unique=True)
    end_date = models.DateField(unique=True)
    exact_working_hours = models.PositiveSmallIntegerField(
        default=40)
    max_working_hours = models.PositiveSmallIntegerField(default=60)
    min_working_hours = models.PositiveSmallIntegerField(default=40)
    holiday_prefills = models.ManyToManyField(
        HolidayPrefills,
        blank=True,
        help_text='Select items to prefill in timecards for this period. To '\
        'create additional items, click the green "+" sign.'
    )
    message = models.TextField(
        help_text='A message to provide at the top of the reporting period. This will appear above any Timecard Notes in a Timecard.',
        blank=True
    )
    message_style = models.CharField(
        choices=USWDS_ALERT_CHOICES,
        default=USWDS_ALERT_INFO,
        max_length=32,
        help_text='The style in which to display the message in a reporting period.'
    )
    message_title = models.CharField(
        blank=True,
        max_length=140,
        help_text='An optional title to appear with the message.'
    )
    message_enabled = models.BooleanField(
        default=False,
        help_text='Toggle whether or not the message is displayed for the specific reporting period and visible in a Timecard.'
    )

    def __str__(self):
        return str(self.start_date)

    class Meta:
        verbose_name = 'Reporting Period'
        verbose_name_plural = 'Reporting Periods'
        get_latest_by = 'start_date'
        unique_together = ('start_date', 'end_date',)
        ordering = ['-start_date']

    def get_message_enabled_display(self):
        if not self.message_enabled:
            return 'Message Disabled'

        return 'Message Enabled'

    def get_fiscal_year(self):
        """Determines the Fiscal Year (Oct 1 - Sept 31) of a given
            ReportingPeriod. Oct, Nov, Dec are part of the *next* FY """
        next_calendar_year_months = [10, 11, 12]
        if self.start_date.month in next_calendar_year_months:
            fiscal_year = self.start_date.year + 1
            return fiscal_year
        else:
            return self.start_date.year

    def get_projects(self):
        """Return the valid projects that exist during this reporting period."""
        rps = self.start_date

        return Project.objects.filter(
            Q(active=True)
            & Q(
                Q(start_date__lte=rps)
                | Q(
                    Q(start_date__gte=rps)
                    & Q(start_date__lte=datetime.datetime.now().date())
                )
                | Q(start_date__isnull=True)
            )
            & Q(
                Q(end_date__gte=rps)
                | Q(end_date__isnull=True)
            )
        )

    def has_holiday_prefills(self):
        return self.holiday_prefills.exists()
    has_holiday_prefills.boolean = True


class Timecard(models.Model):
    user = models.ForeignKey(User, related_name="timecards")
    reporting_period = models.ForeignKey(ReportingPeriod)
    time_spent = models.ManyToManyField(Project, through='TimecardObject')
    submitted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'reporting_period')
        get_latest_by = "reporting_period__start_date"

    def __str__(self):
        return "%s - %s" % (self.user, self.reporting_period.start_date)


class TimecardNoteManager(models.Manager):
    def enabled(self):
        return super(TimecardNoteManager, self).get_queryset().filter(enabled=True)

    def disabled(self):
        return super(TimecardNoteManager, self).get_queryset().filter(enabled=False)


class TimecardNote(models.Model):
    # Alerts will be displayed in the Timecard form using the USWDS themes,
    # which are found here:  https://standards.usa.gov/components/alerts/
    USWDS_ALERT_SUCCESS = 'success'
    USWDS_ALERT_WARNING = 'warning'
    USWDS_ALERT_ERROR = 'error'
    USWDS_ALERT_INFO = 'info'

    USWDS_ALERT_CHOICES = (
        (USWDS_ALERT_INFO, 'Blue (Info)'),
        (USWDS_ALERT_SUCCESS, 'Green (Success)',),
        (USWDS_ALERT_WARNING, 'Yellow (Warning)'),
        (USWDS_ALERT_ERROR, 'Red (Error)'),
    )

    title = models.CharField(
        max_length=140,
        help_text='The heading that will appear above the note when displayed in a timecard.'
    )
    body = models.TextField(
        help_text='The body of the note that will appear when displayed in a timecard.'
    )
    enabled = models.BooleanField(
        default=True,
        help_text='Toggle whether or not the note is displayed in a timecard.'
    )
    style = models.CharField(
        choices=USWDS_ALERT_CHOICES,
        default=USWDS_ALERT_INFO,
        max_length=32,
        help_text='The style in which to display the note in a timecard.'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created on'
    )
    modified = models.DateTimeField(
        auto_now=True,
        verbose_name='Last modified'
    )

    objects = TimecardNoteManager()

    class Meta:
        verbose_name = 'Timecard Note'
        verbose_name_plural = 'Timecard Notes'


    def get_enabled_display(self):
        if not self.enabled:
            return 'Disabled'

        return 'Enabled'

    def __str__(self):
        return '{title} ({enabled} / {style})'.format(
            title=self.title,
            enabled=self.get_enabled_display(),
            style=self.get_style_display()
        )


class TimecardObject(models.Model):
    timecard = models.ForeignKey(Timecard, related_name="timecardobjects")
    project = models.ForeignKey(Project)
    hours_spent = models.DecimalField(decimal_places=2,
                                      max_digits=5,
                                      blank=True,
                                      null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    grade = models.ForeignKey(EmployeeGrade, blank=True, null=True)

    # The notes field is where the user records notes about time spent on
    # certain projects (for example, time spent on general projects).  It may
    # only be display and required when certain projects are selected.
    notes = models.TextField(
        blank=True,
        default='',
        help_text='Please provide details about how you spent your time.'
    )
    submitted = models.BooleanField(default=False)
    revenue_profit_loss_account = models.ForeignKey(
        ProfitLossAccount,
        blank=True,
        null=True,
        related_name='revenue_profit_loss_account_'
    )
    expense_profit_loss_account = models.ForeignKey(
        ProfitLossAccount,
        blank=True,
        null=True,
        related_name='expense_profit_loss_account_'
    )

    def project_alerts(self):
        return self.project.alerts.all()

    def hours(self):
        return self.hours_spent

    def notes_list(self):
        return self.notes.split('\n')

    def save(self, *args, **kwargs):
        """Custom save() method to append employee grade info and the submitted
        status of the related timecard."""

        self.grade = EmployeeGrade.get_grade(
            self.timecard.reporting_period.end_date,
            self.timecard.user
        )

        self.submitted = self.timecard.submitted

        p_pl = self.project.profit_loss_account # Project PL info.
        u_pl = self.timecard.user.user_data.profit_loss_account # User PL info.
        rp = self.timecard.reporting_period # TimecardObject reporting period.

        if p_pl and \
        p_pl.account_type == 'Revenue' and \
        p_pl.as_start_date < rp.end_date and \
        p_pl.as_end_date > rp.end_date:
            self.revenue_profit_loss_account = p_pl
        else:
            self.revenue_profit_loss_account = None

        if u_pl and \
        u_pl.account_type == 'Expense' and \
        u_pl.as_start_date < rp.end_date and \
        u_pl.as_end_date > rp.end_date:

            self.expense_profit_loss_account = u_pl
        else:
            self.expense_profit_loss_account = None


        super(TimecardObject, self).save(*args, **kwargs)
