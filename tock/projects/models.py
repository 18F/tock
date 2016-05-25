from django.db import models


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
    IMPORTANT = 'important'
    NORMAL = ''

    STYLE_CHOICES = (
        (NORMAL, 'Normal'),
        (IMPORTANT, 'Important'),
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

    class Meta:
        verbose_name = 'Project Alert'
        verbose_name_plural = 'Project Alerts'

    @property
    def full_alert(self):
        """ Returns the full string of the alert, accounting for any optional label"""
        if self.label:
            return '%s: %s' % (self.label, self.description)

        return self.description

    def __str__(self):
        return self.title

class Project(models.Model):
    """ Stores information about a specific project"""
    name = models.CharField(max_length=200)
    mbnumber = models.CharField(max_length=200, blank=True, verbose_name="MB Number")
    accounting_code = models.ForeignKey(AccountingCode,
                                        verbose_name="Accounting Code")
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
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

        super(Project, self).save(*args, **kwargs)
