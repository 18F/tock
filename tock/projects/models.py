from django.db import models

# Create your models here.
class Agency(models.Model):
    name = models.CharField(max_length=200)
    department = models.CharField(max_length=200, blank=True)
    omb_agency_code = models.CharField(max_length=3, blank=True)
    omb_bureau_code = models.CharField(max_length=2, blank=True)
    treasury_agency_code = models.CharField(max_length=2, blank=True)
    cgac_agency_code = models.CharField(max_length=3, blank=True)

    class Meta:
        verbose_name = "Agency"
        verbose_name_plural = "Agencies"

class Project(models.Model):
    name = models.CharField(max_length=200)
    iaa = models.CharField(max_length=200, blank=True)
    agency = models.ForeignKey(Agency)

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"