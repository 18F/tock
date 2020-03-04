import datetime

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from employees.models import EmployeeGrade, UserData
from projects.models import ProfitLossAccount, Project
from .utils import ValidateOnSaveMixin, render_markdown


class HolidayPrefills(models.Model):
    """For use with ReportingPeriods to prefill timecards."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    hours_per_period = models.PositiveSmallIntegerField(default=8)

    def __str__(self):
        return '{} ({} hrs.)'.format(self.project.name, self.hours_per_period)

    class Meta:
        verbose_name = 'Holiday Prefills'
        verbose_name_plural = 'Holiday Prefills'
        unique_together = ['project', 'hours_per_period']
        ordering = ['project__name']


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
        help_text='A message to provide at the top of the reporting period. This will appear above any Timecard Notes in a Timecard. Note: supports Markdown.',
        blank=True
    )
    rendered_message = models.TextField(
        help_text='HTML rendered from Markdown in the message field',
        blank=True,
        editable=False
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
        """Determines the Fiscal Year (Oct 1 - Sept 30) of a given
            ReportingPeriod. Oct, Nov, Dec are part of the *next* FY """
        next_calendar_year_months = [10, 11, 12]
        # When this reporting period spans two fiscal years
        if self.start_date.month == 9 and self.end_date.month == 10:
            # if start date is 9/27 or earlier, it means there's more September
            # than October in this period, so it belongs to FY of September
            if self.start_date.day <= 27:
                return self.start_date.year
            # Else there's more October days, it belongs to the FY of October
            else:
                return self.start_date.year + 1

        elif self.start_date.month in next_calendar_year_months:
            fiscal_year = self.start_date.year + 1
            return fiscal_year
        else:
            return self.start_date.year


    @staticmethod
    def get_fiscal_year_start_date(fiscal_year):
        """
        Normally the FY start date is 10/1 of the previous year, but since our
        system makes use of reporting period, we cannot just easily use this
        date.  So in this system, during the week that spans two fiscal years,
        that week will belong to the previous year if there's more September
        days than October. And more October days means it belongs to this year.
        i.e. 10/1/2015 is on a Thursday, this means it belongs to FY 2015 since
        there is more September days that week (Sun to Wed), so the start date
        of FY 2016 is 10/04/2015 (that coming Sunday).
        """
        first_date = datetime.date(fiscal_year - 1, 10, 1)
        # converting definition of weekday for easier calculation,
        # so Sun = 0, Mon = 1, ... Sat = 6
        normalized_weekday = (first_date.weekday() + 1) % 7
        # if 10/1 is Sun=0, Mon=1, Tues=2, or Wed=3
        if normalized_weekday in range(4):
            # this week belongs to this fiscal year
            # so the Sunday is the start of the fiscal year
            # i.e. if Tuesday, this will subtract 2 days to get the Sunday date
            return first_date - datetime.timedelta(days = normalized_weekday)
        else:
            # this week belongs to previous fiscal year
            # so the coming Sunday is the start of the fiscal year
            # i.e. if Thursday, this will add 7 - 4 days (3 days) to get the
            # Sunday date
            return first_date + datetime.timedelta(days = 7 - normalized_weekday)

    @staticmethod
    def get_fiscal_year_end_date(fiscal_year):
        """
        Normally the FY end date is 9/30 of the year, but since our
        system makes use of reporting period, we cannot just easily use this
        date.  So in this system, during the week that spans two fiscal years,
        that week will belong to the year if there's more September
        days than October. And more October days means it belongs to next year.
        i.e. 9/30/2015 is on a Wednesday, this means it belongs to FY 2015 since
        there is more September days that week (Sun to Wed), so the end date
        of FY 2016 is 10/03/2015 (that Sunday) even though it is an October
        day.
        """
        last_date = datetime.date(fiscal_year, 9, 30)
        # converting definition of weekday for easier calculation,
        # so Sun = 0, Mon = 1, ... Sat = 6
        normalized_weekday = (last_date.weekday() + 1) % 7
        # if 9/30 is Sun=0, Mon=1, Tues=2
        if normalized_weekday in range(3):
            # this week belongs to next fiscal year
            # so the Saturday before is the end of the fiscal year
            # i.e. if Tuesday, this will subtract 2+1 = 3 days to get the Saturday
            # date
            return last_date - datetime.timedelta(days = normalized_weekday + 1)
        else:
            # this week belongs to this fiscal year
            # so the coming Saturday is the end of the fiscal year
            # i.e. if Thursday, this will add 6 - 4 days (2 days) to get the
            # Saturday date
            return last_date + datetime.timedelta(days = 6 - normalized_weekday)

    @staticmethod
    def get_fiscal_year_from_date(date):
        fy_end = ReportingPeriod.get_fiscal_year_end_date(date.year)

        if date <= fy_end:
            return date.year
        else:
            return date.year + 1

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

    def save(self, *args, **kwargs):
        if self.message:
           self.rendered_message = render_markdown(self.message)
        super().save(*args, **kwargs)

    @classmethod
    def get_most_recent_periods(cls, number_of_periods=1):
        """
        Return the most recent N completed reporting periods
        A reporting period is complete if it's end date
        has is today or in the past.
        """
        today = datetime.date.today()
        return ReportingPeriod.objects.filter(end_date__lte=today).order_by('-start_date')[:number_of_periods]

class Timecard(models.Model):
    user = models.ForeignKey(User, related_name='timecards', on_delete=models.CASCADE)
    reporting_period = models.ForeignKey(ReportingPeriod, on_delete=models.CASCADE)
    time_spent = models.ManyToManyField(Project, through='TimecardObject')
    submitted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    billable_expectation = models.DecimalField(validators=[MaxValueValidator(limit_value=1)],
                                            default=0.80, decimal_places=2, max_digits=3,
                                            verbose_name="Percentage of hours which are expected to be billable this week")

    # Utilization reporting
    target_hours = models.DecimalField(decimal_places=2, max_digits=5, null=True, blank=True,
                                       verbose_name="# of hours which were expected to be billable")
    billable_hours = models.DecimalField(decimal_places=2, max_digits=5, null=True, blank=True,
                                        verbose_name="# of hours which were billable")
    non_billable_hours = models.DecimalField(decimal_places=2, max_digits=5, null=True, blank=True,
                                            verbose_name="# of hours which were non-billable")
    excluded_hours = models.DecimalField(decimal_places=2, max_digits=5, null=True, blank=True,
                                         verbose_name="# of hours which were excluded from utilization calculations (e.g. Out of office)")
    utilization = models.DecimalField(decimal_places=2, max_digits=5, null=True, blank=True,
                                      verbose_name="Calculated Utilization for this timecard")

    class Meta:
        unique_together = ('user', 'reporting_period')
        get_latest_by = 'reporting_period__start_date'

    def __str__(self):
        return "%s - %s" % (self.user, self.reporting_period.start_date)

    def save(self, *args, **kwargs):
        """
        If this is a new timecard,
        Set weekly billing expectation from user.user_data
        """
        if not self.id and self.user:
            self.billable_expectation = self.user.user_data.billable_expectation
        self.calculate_hours()
        super().save(*args, **kwargs)

    def calculate_utilization_denominator(self):
        return self.billable_hours + self.non_billable_hours

    def calculate_target_hours(self):
        return round(self.billable_expectation * self.calculate_utilization_denominator(), 0)

    def calculate_utilization(self):
        if self.target_hours:
            return self.billable_hours / self.target_hours
        return 0

    def calculate_hours(self):
        billable_filter = Q(timecardobjects__project__accounting_code__billable=True)
        non_billable_filter = Q(timecardobjects__project__accounting_code__billable=False,
                          timecardobjects__project__exclude_from_billability=False)
        excluded_filter = Q(timecardobjects__project__exclude_from_billability=True)

        # Using Coalesce to set a default value of 0 if no data is available
        billable = Coalesce(Sum('timecardobjects__hours_spent', filter=billable_filter), 0)
        non_billable = Coalesce(Sum('timecardobjects__hours_spent', filter=non_billable_filter), 0)
        excluded = Coalesce(Sum('timecardobjects__hours_spent', filter=excluded_filter), 0)

        timecard = Timecard.objects.filter(id=self.id).annotate(billable=billable).annotate(non_billable=non_billable).annotate(excluded=excluded)[0]

        self.billable_hours = round(timecard.billable, 2)
        self.non_billable_hours = round(timecard.non_billable, 2)
        self.excluded_hours = round(timecard.excluded, 2)

        self.target_hours = self.calculate_target_hours()
        self.utilization = self.calculate_utilization()

    def _update_utilization_fields(self):
        self.target_hours = self.calculate_target_hours()
        self.billable_hours = self.calculate_billable_hours()
        self.non_billable_hours = self.calculate_non_billable_hours()
        self.excluded_hours = self.calculate_excluded_hours()
        self.utilization = self.calculate_utilization()

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
        help_text='The body of the note that will appear when displayed in a timecard. Note: supports Markdown.'
    )
    rendered_body = models.TextField(
        help_text='HTML rendered from Markdown in the body field',
        editable=False,
        blank=True
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
    position = models.SmallIntegerField(
        default=0,
        help_text='The order in which this timecard note should be displayed. Note: when creating a new timecard note, this value will be updated automatically upon the first save to be the next available position.'
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
        ordering=['position']
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

    def save(self, *args, **kwargs):
        if not self.pk:
            self.position = TimecardNote.objects.count() + 1
        if self.body:
           self.rendered_body = render_markdown(self.body)
        super(TimecardNote, self).save(*args, **kwargs)

class TimecardObject(models.Model):
    timecard = models.ForeignKey(Timecard, related_name='timecardobjects', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    hours_spent = models.DecimalField(decimal_places=2,
                                      max_digits=5,
                                      blank=True,
                                      null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    grade = models.ForeignKey(EmployeeGrade, blank=True, null=True, on_delete=models.CASCADE)

    # The notes field is where the user records notes about time spent on
    # certain projects (for example, time spent on general projects).  It may
    # only be display and required when certain projects are selected.
    notes = models.TextField(
        blank=True,
        default='',
        help_text='Please provide details about how you spent your time.'
    )
    revenue_profit_loss_account = models.ForeignKey(
        ProfitLossAccount,
        blank=True,
        null=True,
        related_name='revenue_profit_loss_account',
        on_delete=models.CASCADE
    )
    expense_profit_loss_account = models.ForeignKey(
        ProfitLossAccount,
        blank=True,
        null=True,
        related_name='expense_profit_loss_account',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('timecard', 'project')

    def project_alerts(self):
        return self.project.alerts.all()

    def hours(self):
        return self.hours_spent

    def notes_list(self):
        return self.notes.split('\n')

    def __str__(self):
        return f'{self.timecard} {self.project}'

    def save(self, *args, **kwargs):
        """Custom save() method to append employee grade info and the submitted
        status of the related timecard."""

        self.grade = EmployeeGrade.get_grade(
            self.timecard.reporting_period.end_date,
            self.timecard.user
        )

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


    def to_csv_row(self):
        """Output attributes for csv.writer consumption"""
        return [
            "{0} - {1}".format(
                self.timecard.reporting_period.start_date,
                self.timecard.reporting_period.end_date
            ),
            self.timecard.modified.strftime("%Y-%m-%d %H:%M:%S"),
            self.timecard.user.username,
            self.project,
            self.hours_spent,
            self.timecard.user.user_data.organization_name,
            self.project.organization_name
        ]

class TimecardPrefillDataManager(models.Manager):
    def active(self):
        return super(TimecardPrefillDataManager, self).get_queryset().filter(
            is_active=True
        )

    def inactive(self):
        return super(TimecardPrefillDataManager, self).get_queryset().filter(
            is_active=False
        )


class TimecardPrefillData(models.Model):
    employee = models.ForeignKey(UserData, related_name='timecard_prefill_data', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='timecard_prefill_data', on_delete=models.CASCADE)
    hours = models.DecimalField(
        decimal_places=2,
        max_digits=5,
        help_text='The amount of hours this user is assigned to this project.'
    )
    notes = models.TextField(
        blank=True,
        default='',
        help_text='Any additional notes specific to this assignment.'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Toggle whether or not this record is active and used.'
    )
    start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Start Date',
        help_text='Optional start date for when this record should be used.'
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='End Date',
        help_text='Optional end date for when this record should no longer be used.'
    )

    objects = TimecardPrefillDataManager()

    class Meta:
        unique_together = ('employee', 'project')
        verbose_name = 'Timecard Prefill Data'
        verbose_name_plural = 'Timecard Prefill Data'

    def __str__(self):
        return '{} - {} ({})'.format(self.employee, self.project, self.hours)
