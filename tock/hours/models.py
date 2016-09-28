import datetime

from .utils import ValidateOnSaveMixin
from projects.models import Project

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Q, Sum


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
    target_billable_hours = models.PositiveIntegerField(blank=True, null=True)

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
        rps = self.start_date

        return Project.objects.filter(
            Q(active=True)
            & Q(
                Q(start_date__lte=rps)
                | Q(
                    Q(start_date__gte=rps)
                    & Q(start_date__lte=datetime.datetime.now().date())
                )
                | Q(start_date__isnull=True)
            )
            & Q(
                Q(end_date__gte=rps)
                | Q(end_date__isnull=True)
            )
        )

    def recent_performance(self):
        date_range = 45
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=date_range)

        perf_rps = ReportingPeriod.objects.filter(
            start_date__gte=start_date,
            end_date__lte=end_date
        )

        plan = perf_rps.aggregate(Sum('target_billable_hours'
            )
        )['target_billable_hours__sum']

        if plan:
            performance = TimecardObject.objects.filter(
                timecard__reporting_period__start_date__gte=start_date,
                timecard__reporting_period__end_date__lte=end_date,
            ).aggregate(Sum('hours_spent'))['hours_spent__sum']

            try:
                percentage = '{:.0%}'.format(performance / plan)
            except TypeError:
                return None

            return 'During the prior {} reporting periods, we logged {} ' \
            'billable hours. This is {} of our target, {} hours.'.format(
                len(perf_rps),
                int(performance),
                percentage,
                plan
            )
        else:
            return None

class Timecard(models.Model):
    user = models.ForeignKey(User)
    reporting_period = models.ForeignKey(ReportingPeriod)
    time_spent = models.ManyToManyField(Project, through='TimecardObject')
    submitted = models.BooleanField(default=False)
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
    submitted = models.BooleanField(default=False)

    def project_alerts(self):
        return self.project.alerts.all()

    def hours(self):
        return self.hours_spent

    def notes_list(self):
        return self.notes.split('\n')

    def save(self, *args, **kwargs):
        self.submitted = self.timecard.submitted

        super(TimecardObject, self).save(*args, **kwargs)
