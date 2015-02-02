from django.core.validators import MaxValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

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
    user = models.ForeignKey(User)
    week = models.ForeignKey(Week)
    time_spent = models.ManyToManyField(Project, through='TimecardObject')

    class Meta:
        unique_together = ('user', 'week')

class TimecardObject(models.Model):
    timecard = models.ForeignKey(Timecard)
    project = models.ForeignKey(Project)
    time_percentage = models.DecimalField(decimal_places=2, max_digits=3, validators=[MaxValueValidator(1)])
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
