from django.contrib.auth.models import User
from django.db import models, IntegrityError
from django.db.models import Q, Max
from django.apps import apps

from rest_framework.authtoken.models import Token

from projects.models import ProfitLossAccount

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
        help_text='Please select from existing employees.',
        unique_for_date='g_start_date',
    )
    grade = models.IntegerField(
        choices=GRADE_CHOICES,
        help_text='Please select a GS grade level.'
    )
    g_start_date = models.DateField(
        help_text='Please select a start date for this grade.',
        verbose_name='Grade start date'
    )

    def __str__(self):
        return '{0} - {1} (Starting: {2})'.format(self.employee, self.grade, self.g_start_date)

    def save(self, *args, **kwargs):
        if EmployeeGrade.objects.filter(g_start_date=self.g_start_date):
            raise IntegrityError
        super(EmployeeGrade, self).save(*args, **kwargs)
        # Lazily load the TimecardObject model, find pertinent objects and save
        # to update w/ relevant grade info.
        update = [ t.save() for t in \
            apps.get_model('hours', 'TimecardObject').objects.filter(
                timecard__user=self.employee,
                timecard__reporting_period__start_date__gte=self.g_start_date
        ) ]

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
    profit_loss_account = models.ForeignKey(
        ProfitLossAccount,
        blank=True,
        null=True,
        verbose_name='Profit/loss Accounting String'
    )
    class Meta:
        verbose_name='Employee'
        verbose_name_plural='Employees'

    def __str__(self):
        return '%s' % (self.user)

    def save(self, *args, **kwargs):
        """Aligns User model and UserData model attributes on save."""
        user = User.objects.get(username=self.user)
        if self.current_employee:
            user.is_active = True
        else:
            user.is_active = False
            user.is_superuser = False
            user.is_staff = False
            user.save()
            try:
                token = Token.objects.get(user=self.user)
                token.delete()
            except Token.DoesNotExist:
                pass
        user.save()

        super(UserData, self).save(*args, **kwargs)
