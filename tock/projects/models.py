from django.db import models

# Create your models here.
class Agency(models.Model):
    name = models.CharField(max_length=200, verbose_name="Name")
    department = models.CharField(max_length=200, blank=True, verbose_name="Department")
    omb_agency_code = models.CharField(max_length=3, blank=True, verbose_name="OMB Agency Code")
    omb_bureau_code = models.CharField(max_length=2, blank=True, verbose_name="OMB Bureau Code")
    treasury_agency_code = models.CharField(max_length=2, blank=True, verbose_name="Treasury Agency Code")
    cgac_agency_code = models.CharField(max_length=3, blank=True, verbose_name="CGAC Agency Code")

    class Meta:
        verbose_name = "Agency"
        verbose_name_plural = "Agencies"

    def __str__(self):
        if self.department:
            return '%s | %s' % (self.name, self.department)
        else:
            return '%s' % (self.name)

class Project(models.Model):
    name = models.CharField(max_length=200)
    iaa = models.CharField(max_length=200, blank=True)
    agency = models.ForeignKey(Agency)
    description = models.TextField(blank=True, null=True)
    billable = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return '%s' % (self.name)