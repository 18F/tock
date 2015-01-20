from django.core.validators import MaxValueValidator
from django.db import models

# Create your models here.
class Week(models.Model):
    startddate = models.DateField()
    enddate = models.DateField()
    working_hours = models.PositiveSmallIntegerField(default=40,
                            validators=[MaxValueValidator(40)])
