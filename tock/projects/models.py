from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from organizations.models import Organization


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
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)
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
    """ Contains information that can be displayed as an alert related to a project line item."""
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
        help_text='A title to describe the alert so it can be found when linking it to a project.'
    )
    label = models.CharField(
        max_length=64,
        blank=True,
        help_text='An optional short label to precede the description, e.g., "Note", "Reminder", etc.'
    )
    description = models.TextField(
        help_text='The text that is displayed as the note description under a project line item.'
    )
    style = models.CharField(
        max_length=32,
        blank=True,
        choices=STYLE_CHOICES,
        default=NORMAL,
        help_text='An optional style option to change the display and formatting of the alert.'
    )
    style_bold = models.BooleanField(
        default=False,
        help_text='A toggle for whether or not the alert should also be bold. Not applicable when no style is selected.'
    )
    style_italic = models.BooleanField(
        default=False,
        help_text='A toggle for whether or not the alert should also be italicized. Not applicable when no style is selected.'
    )
    destination_url = models.URLField(
        max_length=512,
        blank=True,
        help_text='An optional URL to wrap the alert in, e.g. pointing to some additional documentation around a time tracking policy.'
    )

    class Meta:
        verbose_name = 'Project Alert'
        verbose_name_plural = 'Project Alerts'

    @property
    def full_alert_text(self):
        """ Returns the full string of the alert, accounting for any optional label"""
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

class ProfitLossAccount(models.Model):
    """ The profit and loss account where revenue is counted"""
    name = models.CharField(
        max_length=200
    )
    accounting_string = models.CharField(
        max_length=200, verbose_name='Accounting String'
    )
    as_start_date = models.DateField(
        blank=True, null=True, verbose_name='Start Date'
    )
    as_end_date = models.DateField(
        blank=True, null=True, verbose_name='End Date'
    )
    account_type = models.CharField(
        choices=[('Revenue','Revenue'), ('Expense', 'Expense')],
        default='Revenue',
        max_length=200
    )

    def __str__(self):
        start_date = 'N/A'
        end_date = 'N/A'

        if self.as_start_date:
            start_date = '{}/{}'.format(
                self.as_start_date.month,
                self.as_start_date.year
            )

        if self.as_end_date:
            end_date = '{}/{}'.format(
                self.as_end_date.month,
                self.as_end_date.year
            )

        return '{} - {} ({} - {})'.format(
            self.name,
            self.account_type,
            start_date,
            end_date
        )


class ProjectManager(models.Manager):
    """
    Provides convenience methods for filtering Project models.

    Also, not to be confused with a human in a similarly named role. :-)
    """

    def get_queryset(self):
        return super().get_queryset().order_by('name')

    def active(self):
        return self.get_queryset().filter(active=True)

    def inactive(self):
        return self.get_queryset().filter(active=False)

    # Get the projects that are categorized as excluded from billability, i.e. out of office, which means
    # the hours tocked in these projects will not be used in the total hours calculation when tryng to figure
    # out how many hours should be billable in a reporting period.
    def excluded_from_billability(self):
        return self.get_queryset().filter(exclude_from_billability=True)

    # Get the projects that are categorized as nonbillable, which means the hours tocked in these projects
    # will be used in the total hourse calcuation when trying to figure out how many hours should be billable
    # in a reporting period.
    def non_billable(self):
        return self.get_queryset().filter(exclude_from_billability=False, accounting_code__billable=False)


class Project(models.Model):
    """
    Stores information about a specific project
    """
    name = models.CharField(max_length=200)
    mbnumber = models.CharField(max_length=200, blank=True, verbose_name="MB Number")
    accounting_code = models.ForeignKey(
        AccountingCode,
        on_delete=models.CASCADE,
        verbose_name="Accounting Code"
    )
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True, verbose_name='Project Start Date')
    end_date = models.DateField(blank=True, null=True, verbose_name='Project End Date')
    active = models.BooleanField(default=True)
    notes_required = models.BooleanField(
        default=False,
        verbose_name="Notes are required",
        help_text='Check if notes should be required for time entries against this project. Note: Checking this enables notes display as well.'
    )
    notes_displayed = models.BooleanField(
        default=False,
        verbose_name="Notes are requested (not required)",
        help_text='Check this if a notes field should be displayed along with a time entry against a project.'
    )
    alerts = models.ManyToManyField(
        ProjectAlert,
        blank=True,
        help_text='Attach one or more alerts to be displayed with this project if need be.'
    )
    agreement_URL = models.URLField(
        blank=True,
        max_length=1000,
        verbose_name="Link to Agreement Folder"
    )
    profit_loss_account = models.ForeignKey(
        ProfitLossAccount,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Profit/loss Accounting String'
    )
    project_lead = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, blank=True, null=True, on_delete=models.CASCADE)
    exclude_from_billability = models.BooleanField(
        default=False,
        help_text='Check if this project should be excluded from calculations of billable hours, e.g. Out of Office'
    )
    objects = ProjectManager()

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ('name',)

    def __str__(self):
        return '%s - %s' % (self.id, self.name)

    def is_billable(self):
        return self.accounting_code.billable

    def get_profit_loss_account(self):
        if self.profit_loss_account:
            return self.profit_loss_account.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('ProjectView', args=[str(self.id)])

    @property
    def organization_name(self):
        """
        Returns the organization name associated with the project or an
        empty string if no organization is set.
        """
        if self.organization is not None:
            return self.organization.name

        return ''

    def clean(self):
        if self.accounting_code.billable and self.organization is None:
            raise ValidationError('You must specify an organization for billable projects.')

    def save(self, *args, **kwargs):
        if self.notes_required:
            self.notes_displayed = True

        super(Project, self).save(*args, **kwargs)
