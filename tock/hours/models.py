import datetime

from django.core.validators import MaxValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

from .utils import ValidateOnSaveMixin, number_of_hours
from projects.models import Project


# Create your models here.
class ReportingPeriod(ValidateOnSaveMixin, models.Model):
  start_date = models.DateField()
  end_date = models.DateField()
  working_hours = models.PositiveSmallIntegerField(
      default=40,
      validators=[MaxValueValidator(40)])

  def __str__(self):
    return str(self.start_date)

  class Meta:
    verbose_name = "Reporting Period"
    verbose_name_plural = "Reporting Periods"
    get_latest_by = "start_date"

  def get_fiscal_year(self):
    """Determines the Fiscal Year (Oct 1 - Sept 31) of a given
        ReportingPeriod"""
    # Oct, Nov, Dec are part of the *next* FY
    next_calendar_year_months = [10, 11, 12]
    if self.start_date.month in next_calendar_year_months:
      fiscal_year = self.start_date.year + 1
      return fiscal_year
    else:
      return self.start_date.year


class Timecard(models.Model):
  user = models.ForeignKey(User)
  reporting_period = models.ForeignKey(ReportingPeriod)
  time_spent = models.ManyToManyField(Project, through='TimecardObject')
  created = models.DateTimeField(auto_now_add=True)
  modified = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = ('user', 'reporting_period')
    get_latest_by = "reporting_period__start_date"

  def __str__(self):
    return "%s - %s" % (self.user, self.reporting_period.start_date)


class TimecardObject(models.Model):
  timecard = models.ForeignKey(Timecard)
  project = models.ForeignKey(Project)
  time_percentage = models.DecimalField(decimal_places=1,
                                        max_digits=4,
                                        validators=[MaxValueValidator(100)],
                                        blank=True,
                                        null=True)
  hours_spent = models.DecimalField(decimal_places=2,
                                    max_digits=4,
                                    blank=True,
                                    null=True)
  created = models.DateTimeField(auto_now_add=True)
  modified = models.DateTimeField(auto_now=True)

  def hours(self):
    return self.hours_spent
