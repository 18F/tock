from django.db import models
from datetime import date, timedelta


class Agency(models.Model):
    """ Stores Agency name """
    name = models.CharField(
        max_length=200,
        verbose_name="Name",
        help_text="Don't make crappy names!")

    class Meta:
        verbose_name = "Agency"
        verbose_name_plural = "Agencies"

    def __str__(self):
        return '%s' % (self.name)


class AccountingCode(models.Model):
    """ Account code for each project """
    code = models.CharField(max_length=200, blank=True)
    agency = models.ForeignKey(Agency)
    office = models.CharField(max_length=200, blank=True)
    billable = models.BooleanField(default=False)
    flat_rate = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Accounting Code"
        verbose_name_plural = "Accounting Codes"
        ordering = ('agency', 'office')

    def __str__(self):
        if self.office:
            if self.code:
                return '%s - %s (%s)' % (self.agency, self.office, self.code)
            else:
                return '%s - %s' % (self.agency, self.office)
        else:
            if self.code:
                return "%s (%s)" % (self.agency, self.code)
            else:
                return "%s" % (self.agency)


class ProjectAlert(models.Model):
    """ Contains information that can be displayed as an alert related to a
    project line item.
    """
    NORMAL = ''
    INFO = 'info'
    IMPORTANT = 'important'
    WARNING = 'warning'

    STYLE_CHOICES = (
        (NORMAL, 'No style'),
        (INFO, 'Info'),
        (IMPORTANT, 'Important'),
        (WARNING, 'Warning'),
    )

    title = models.CharField(
        max_length=128,
        help_text='A title to describe the alert so it can be found when '
        'linking it to a project.'
    )
    label = models.CharField(
        max_length=64,
        blank=True,
        help_text='An optional short label to precede the description, e.g., '
        '"Note", "Reminder", etc.'
    )
    description = models.TextField(
        help_text='The text that is displayed as the note description under a '
        'project line item.'
    )
    style = models.CharField(
        max_length=32,
        blank=True,
        choices=STYLE_CHOICES,
        default=NORMAL,
        help_text='An optional style option to change the display and '
        'formatting of the alert.'
    )
    style_bold = models.BooleanField(
        default=False,
        help_text='A toggle for whether or not the alert should also be bold. '
        'Not applicable when no style is selected.'
    )
    style_italic = models.BooleanField(
        default=False,
        help_text='A toggle for whether or not the alert should also be '
        'italicized. Not applicable when no style is selected.'
    )
    destination_url = models.URLField(
        max_length=512,
        blank=True,
        help_text='An optional URL to wrap the alert in, e.g. pointing to some '
        'additional documentation around a time tracking policy.'
    )

    class Meta:
        verbose_name = 'Project Alert'
        verbose_name_plural = 'Project Alerts'

    @property
    def full_alert_text(self):
        """
        Returns the full string of the alert, accounting for any optional label.
        """
        if self.label:
            return '%s: %s' % (self.label, self.description)

        return self.description

    @property
    def full_style(self):
        style = self.style

        if self.style_bold:
            style += ' bold'

        if self.style_italic:
            style += ' italic'

        return style

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.style == self.NORMAL:
            self.style_bold = False
            self.style_italic = False

        super(ProjectAlert, self).save(*args, **kwargs)

class Project(models.Model):
    """
    The Project model stores information about a specific project
    """
    name = models.CharField(max_length=200)

    """
    The mbnumber attribute holds a unique identifier required for financial
    processing.
    """
    mbnumber = models.CharField(max_length=200, blank=True, verbose_name="MB Number")

    accounting_code = models.ForeignKey(AccountingCode,
        verbose_name="Accounting Code")

    description = models.TextField(default='If your reading this, a description'
    ' for this project is missing and should be added.')

    """
    The start_date attribute holds the start date value of the project. Value is
    used to evaluate whether the project is made available to the end user.
    """
    start_date = models.DateField(blank=True, null=True,
        verbose_name='Project Start Date')

    """
    Model attribute end_date includes both default value (2020-12-17) for new projects created
    (whether automatically via tests or in production by user) and null=True
    for projects that already exist in the production DB that do not have
    end_dates.
    """
    end_date = models.DateField(default=date(2020, 12, 31),
        verbose_name='Project End Date', null=True)

    """
    Model attribute auto_deactivate_date is automatically calculated based on
    the end_date and the auto_deactivate_days via the save() function. Default
    is set because a non-blank, non-null value is required for legacy data.
    """
    auto_deactivate_date = models.DateField(default=date(2020, 12, 17),
        verbose_name='Early warning deactivation date', help_text= 'The date'
        ' on which the project will no longer be available to log hours against'
        '. This date is calculated based on the end date of the project and the'
        ' early warning days value. Default is December 17, 2020.')

    """
    Model attribute auto_deactivate_days allows the user to set the number of
    days prior to the end date of a project on which this project should no
    longer be available to log hous against.
    """
    auto_deactivate_days = models.IntegerField(default=14, verbose_name='Set '
        'early warning days', help_text='Set the number of calendar days prior '
        'to the end date when this project will no longer be available to log '
        'hours against. Default is 14 days.')

    active = models.BooleanField(default=True, help_text='The active / inactive'
        ' status of this project is based on the start date, end date, early '
        'warning values, maximum hour ceiling, and all time hours logged for '
        'this project and cannot be manually set.')

    """
    Model attribute max_hours allows the user to establish an hours 'ceiling'
    that may be used (see max_hours_restriction attribute) to prevent users from
    logging time to a project that has reached this ceiling.
    """
    max_hours = models.DecimalField(max_digits=10, decimal_places=2,
        default=0.00, null=True, blank=True,
        verbose_name='Maximum hour ceiling', help_text='When set and "Limit'
        ' to maximum hours" is checked, this project will deactivate when this '
        'ceiling is reached.')

    """
    Model attribute max_hours_restriction allows the user to set whether or
    notes the max_hours value is enforced.
    """
    max_hours_restriction = models.BooleanField(default=False,
        verbose_name='Limit to maximum hours', help_text='Check this to enforce'
        ' the maximum hours ceiling.')

    """
    Model attribute aggregate_hours_logged holds a value equal to all
    TimecardObject hours_spent attribute values that have been saved users.
    """
    aggregate_hours_logged = models.DecimalField(max_digits=10,
        decimal_places=2, default=0.00, null=True, blank=True,
        verbose_name='All time hours logged', help_text='All hours logged by '
        'users over all reporting periods.')


    notes_required = models.BooleanField(
        default=False,
        help_text='Check this if notes should be required for time entries against this project.  Note:  Checking this will enable notes to be displayed as well.'
    )
    notes_displayed = models.BooleanField(
        default=False,
        help_text='Check this if a notes field should be displayed along with a time entry against a project.'
    )
    alerts = models.ManyToManyField(
        ProjectAlert,
        blank=True,
        help_text='Attach one or more alerts to be displayed with this project if need be.'
    )

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ('name',)

    def __str__(self):
        return '%s' % (self.name)

    def is_billable(self):
        return self.accounting_code.billable

    def save(self, *args, **kwargs):
        if self.notes_required:
            self.notes_displayed = True

        self.auto_deactivate_date = self.end_date - timedelta(days=self.auto_deactivate_days)

        if date.today() >= self.auto_deactivate_date:
            self.active = False

        elif self.max_hours_restriction == True:
            if self.aggregate_hours_logged >= self.max_hours:
                self.active = False
            else:
                self.active = True
        else:
            self.active = True
            super(Project, self).save(*args, **kwargs)
