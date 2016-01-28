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
