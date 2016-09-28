import datetime

from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.db.models import Q, Max


class EmployeeGrade(models.Model):
    GRADE_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
        (6, '6'),
        (7, '7'),
        (8, '8'),
        (9, '9'),
        (10, '10'),
        (11, '11'),
        (12, '12'),
        (13, '13'),
        (14, '14'),
        (15, '15'),
        (16, 'SES')
    )
    employee = models.ForeignKey(
        User,
        help_text='Please select from existing employees.'
    )
    grade = models.IntegerField(
        choices=GRADE_CHOICES,
        help_text='Please select a GS grade level.',
        unique_for_date='g_start_date'
    )
    g_start_date = models.DateField(
        help_text='Please select a start date for this grade.',
        verbose_name='Grade start date'
    )

    def __str__(self):
        return '{0} - {1} (Starting: {2})'.format(self.employee, self.grade, self.g_start_date)

    def get_grade(end_date, user):
        """Gets grade information based on a date and user. Original use of
        function is to append correct grade information to each
        TimecardObject."""
        queryset = EmployeeGrade.objects.filter(
                Q(employee = user)
                & Q(g_start_date__lte = end_date)
                ).all()
        if queryset:
            return queryset.latest('g_start_date')
        else:
            return None


from hours.models import TimecardObject, ReportingPeriod

class UserData(models.Model):

    UNIT_CHOICES = (
        (0, 'Operations-Team Operations'),
        (1, 'Operations-Talent'),
        (2, 'Operations-Infrastructure'),
        (3, 'Operations-Front Office'),
        (4, 'Chapters-Acquisition Managers'),
        (5, 'Chapters-Engineering'),
        (6, 'Chapters-Experience Design'),
        (7, 'Chapters-Product'),
        (8, 'Chapters-Strategists'),
        (9, 'Business-Acquisition Services'),
        (10, 'Business-Custom Partner Solutions'),
        (11, 'Business-Learn'),
        (12, 'Business-Products & Platforms'),
        (13, 'Business-Transformation Services'),
        (14, 'PIF-Fellows'),
        (15, 'PIF-Operations'),
        (16, 'Unknown / N/A')
    )

    user = models.OneToOneField(User, related_name='user_data', verbose_name='Tock username')
    start_date = models.DateField(blank=True, null=True, verbose_name='Employee start date')
    end_date = models.DateField(blank=True, null=True, verbose_name='Employee end date')
    current_employee = models.BooleanField(default=True, verbose_name='Is Current Employee')
    is_18f_employee = models.BooleanField(default=True, verbose_name='Is 18F Employee')
    is_billable = models.BooleanField(default=True, verbose_name="Is 18F Billable Employee")
    unit = models.IntegerField(null=True, choices=UNIT_CHOICES, verbose_name="Select 18F unit", blank=True)

    class Meta:
        verbose_name='Employee'
        verbose_name_plural='Employees'

    def __str__(self):
        return '{0}'.format(self.user)


    def get_supervisees(self):
        return UserData.objects.filter(supervisor=self.user)

    def get_timecard_objects(self):
        tos = TimecardObject.objects.filter(timecard__user=self.user, timecard__submitted=True)
        return tos

    def get_lifetime_utilization(self):
        tos = self.get_timecard_objects()
        all_hours = tos.all().aggregate(
            Sum('hours_spent'))['hours_spent__sum']
        if all_hours:
            billable_hours = tos.all().filter(
                project__accounting_code__billable=True).all().aggregate(
                Sum('hours_spent'))['hours_spent__sum']
            utilization = '{:.3}%'.format((billable_hours / all_hours)*100)
            return utilization
        else:
            return 'No hours recorded.'

    def get_last_weeks_utlization(self):
        date = datetime.date.today()
        rp = ReportingPeriod.objects.filter(
            end_date__lte=date).latest(
            'timecard__reporting_period__start_date').start_date
        tos = self.get_timecard_objects().all().filter(
            timecard__reporting_period__start_date=rp)
        all_hours = tos.all().aggregate(
            Sum('hours_spent'))['hours_spent__sum']
        if all_hours:
            billable_hours = tos.all().filter(
                project__accounting_code__billable=True).all().aggregate(
                Sum('hours_spent'))['hours_spent__sum']
            lst_wk_utilization = '{:.3}%'.format((billable_hours / all_hours)*100)
            return lst_wk_utilization
        else:
            return 'No hours recorded'

    def save(self, *args, **kwargs):
        if self.current_employee is False:
            try:
                token = Token.objects.get(user=self.user)
                token.delete()
            except Token.DoesNotExist:
                pass
        if self.is_supervisor is False:
            try:
                UserData.objects.filter(supervisor=self.user).update(supervisor=None)
            except UserData.DoesNotExist:
                pass
        super(UserData, self).save(*args, **kwargs)
