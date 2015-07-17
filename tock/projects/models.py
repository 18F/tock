from django.db import models
from django.conf import settings
from django.db.models.loading import get_model


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

    def save(self, *args, **kwargs):
        created = self.pk is None
        super(Project, self).save(*args, **kwargs)
        if created:
            ReportingPeriod = get_model('hours.ReportingPeriod')
            ProjectPeriod = get_model('hours.ProjectPeriod')
            last_period = ReportingPeriod.objects.order_by('-start_date').first()
            if last_period is not None:
                ProjectPeriod.objects.create(
                    project=self,
                    reporting_period=last_period,
                    accounting_code_id=settings.DEFAULT_ACCOUNTING_CODE,
                    active=True,
                )

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return '%s' % (self.name)

    def is_billable(self):
        return self.accounting_code.billable
