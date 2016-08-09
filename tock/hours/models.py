import datetime

from .utils import ValidateOnSaveMixin
from projects.models import Project

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Q


class ReportingPeriod(ValidateOnSaveMixin, models.Model):
    """Reporting period model details"""
    start_date = models.DateField(unique=True)
    end_date = models.DateField(unique=True)
    exact_working_hours = models.PositiveSmallIntegerField(
        default=40)
    max_working_hours = models.PositiveSmallIntegerField(default=60)
    min_working_hours = models.PositiveSmallIntegerField(default=40)
    message = models.TextField(
        help_text='A message to provide at the top of the reporting period.',
        blank=True)

    def __str__(self):
        return str(self.start_date)

    class Meta:
        verbose_name = "Reporting Period"
        verbose_name_plural = "Reporting Periods"
        get_latest_by = "start_date"
        unique_together = ("start_date", "end_date")
        ordering = ['-start_date']

    def get_fiscal_year(self):
        """Determines the Fiscal Year (Oct 1 - Sept 31) of a given
            ReportingPeriod. Oct, Nov, Dec are part of the *next* FY """
        next_calendar_year_months = [10, 11, 12]
        if self.start_date.month in next_calendar_year_months:
            fiscal_year = self.start_date.year + 1
            return fiscal_year
        else:
            return self.start_date.year

    def get_projects(self):
        """Return the valid projects that exist during this reporting period."""
        rps = self.start_date # Reporting period start date
        rpe = self.end_date # Reporting period end date

        return Project.objects.filter(
            Q(active=True) # Projects that are active;
            & Q( # and
                Q(start_date__lte=rpe) # projects that have a start date LTE the reporting period end date;
                | Q(start_date__isnull=True) # or projects do not have start dates;
             )
            & Q( # and
                Q(end_date__gte=rps) # projects that have an end date that is greater than the start date of the reporting period;
                & Q(auto_deactivate_date__gte=rps) # and projects that have an auto deactivate end date that is greater than the reporting period start date;
                )
                | Q(end_date__isnull=True) # or projects that do not have an end date.
             )

class Timecard(models.Model):
    user = models.ForeignKey(User)
    reporting_period = models.ForeignKey(ReportingPeriod)
    time_spent = models.ManyToManyField(Project, through='TimecardObject')
    submitted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    timecard_object_submitted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'reporting_period')
        get_latest_by = "reporting_period__start_date"

    def __str__(self):
        return "%s - %s" % (self.user, self.reporting_period.start_date)


class TimecardObject(models.Model):
    timecard = models.ForeignKey(Timecard)
    project = models.ForeignKey(Project)
    hours_spent = models.DecimalField(decimal_places=2,
                                      max_digits=5,
                                      blank=True,
                                      null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    # The notes field is where the user records notes about time spent on
    # certain projects (for example, time spent on general projects).  It may
    # only be display and required when certain projects are selected.
    notes = models.TextField(
        blank=True,
        default='',
        help_text='Please provide details about how you spent your time.'
    )

    def project_alerts(self):
        return self.project.alerts.all()

    def hours(self):
        return self.hours_spent

    def notes_list(self):
        return self.notes.split('\n')


    def save(self, *args, **kwargs):

        """
        Fetches and saves submitted attribute of TimecardObject to match that of
         the corresponding Timecard submitted attribute.
        """
        self.timecard_object_submitted = self.timecard.submitted
        super(TimecardObject, self).save(*args, **kwargs)

        """
        If submitted attribute is True, uses hours_spent attribute from
        TimecardObjects to update the aggregate_hours_logged attribute of the
        Project model.
        """
        #TODO: issue with class TestAggregates(WebTest): in api tests. seems to be
        # with the TimecardObjectFactory and the way it interacts with the following
        # commands. Note that API tests rely on Factory Boy instead of hard
        # coded test cases.

        if self.timecard_object_submitted == True:
            total_hours = 0
            timecard_object_queryset = TimecardObject.objects.filter(project=self.project)
            for timecard_object in timecard_object_queryset:
                total_hours = total_hours + timecard_object.hours_spent
            Project.objects.select_related().filter(
                name=self.project).update(aggregate_hours_logged=total_hours)

        # end todo.

        """
        Fetches Project queryset, checks to see if the latest addition to
        the aggregate_hours_logged attribute (see above) requires an update
        to the active attribute of that Project. If it does, the update is made.
        """
        project_queryset = Project.objects.get(name=self.project)

        if self.timecard_object_submitted == True:
            if project_queryset.max_hours_restriction == True:
                if project_queryset.aggregate_hours_logged >= project_queryset.max_hours:
                        Project.objects.select_related().filter(
                            name=timecard_object_project_name).update(active=False)
