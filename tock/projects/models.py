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
    investment = models.BooleanField(default=False)

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
    accounting_code = models.ForeignKey(AccountingCode,
                                        verbose_name="Accounting Code")
    description = models.TextField(blank=True, null=True)
    mb_number = models.CharField(max_length=200)
    active = models.BooleanField(blank=True)

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return '%s' % (self.name)

    def is_billable(self):
        return self.accounting_code.billable
