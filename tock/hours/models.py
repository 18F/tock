from django.core.validators import MaxValueValidator
from django.core.exceptions import ValidationError
from django.db import models

from projects.models import Project

# Create your models here.
class Week(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    working_hours = models.PositiveSmallIntegerField(default=40,
                            validators=[MaxValueValidator(40)])

    def __str__(self):
        return str(self.start_date)

class Timecard(models.Model):
    email = models.EmailField(max_length=254)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    week = models.ForeignKey(Week)
    time_spent = models.ManyToManyField(Project, through='TimecardObject')

class TimecardObject(models.Model):
    timecard = models.ForeignKey(Timecard)
    project = models.ForeignKey(Project)
    time_percentage = models.DecimalField(decimal_places=2, max_digits=3)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
