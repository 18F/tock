import datetime
from decimal import Decimal

# DEFAULT_ORG_ID to correspond to '18F'
DEFAULT_ORG_ID = 1

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from django.db import IntegrityError, models
from django.db.models import Q
from organizations.models import Organization, Unit
from projects.models import ProfitLossAccount
from rest_framework.authtoken.models import Token

User = get_user_model()

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
        on_delete=models.CASCADE,
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

    def save(self, *args, **kwargs):
        queryset = EmployeeGrade.objects.filter(
            employee=self.employee,
            g_start_date=self.g_start_date
        )
        if queryset:
            raise IntegrityError(
                'Employee cannot have multiple EmployeeGrade objects with the '\
                'same g_start_date.'
            )
        super(EmployeeGrade, self).save(*args, **kwargs)


class UserData(models.Model):
    user = models.OneToOneField(User, related_name='user_data', verbose_name='Tock username', on_delete=models.CASCADE)
    start_date = models.DateField(blank=True, null=True, verbose_name='Employee start date')
    end_date = models.DateField(blank=True, null=True, verbose_name='Employee end date')
    current_employee = models.BooleanField(default=True, verbose_name='Is Current Employee')
    is_18f_employee = models.BooleanField(default=True, verbose_name='Is 18F Employee')
    billable_expectation = models.DecimalField(validators=[MaxValueValidator(limit_value=1)],
                                             default=Decimal(0.80), decimal_places=2, max_digits=3,
                                             verbose_name="Percentage of hours (expressed as a decimal) expected to be billable each week")
    profit_loss_account = models.ForeignKey(
        ProfitLossAccount,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Profit/loss Accounting String'
    )

    is_aws_eligible = models.BooleanField(
        default=False,
        verbose_name='Is alternative work schedule eligible'
    )
    organization = models.ForeignKey(Organization, default=DEFAULT_ORG_ID, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, blank=True, null=True, on_delete=models.CASCADE,
        verbose_name="Business Unit",
        help_text="The business unit within the organization in which this person sits."
    )

    class Meta:
        verbose_name='Employee'
        verbose_name_plural='Employees'

    def __str__(self):
        return '{0}'.format(self.user)

    @property
    def is_billable(self):
        """
        True if user is currently expected to bill more
        than 0 hours in a regular work week
        """
        return self.billable_expectation > Decimal(0.0)

    @property
    def organization_name(self):
        """
        Returns the organization name associated with the employee or an
        empty string if no organization is set.
        """
        if self.organization is not None:
            return self.organization.name

        return ''

    @property
    def is_late(self):
        """
        Checks if user has a timecard submitted for the
        most recent Reporting Period.

        We're using get_model() to avoid circular imports
        since so many things use UserData.

        If they're not billable staff, they don't have to tock,
        so we'll just bail out.
        """
        if not self.current_employee or not self.is_billable:
            return False
        # They are billable, so go ahead with other checks.
        RP_model = apps.get_model('hours', 'ReportingPeriod')
        TC_model = apps.get_model('hours', 'Timecard')
        rp = RP_model.objects.order_by('end_date').filter(
            end_date__lt=datetime.date.today()
        ).latest()
        timecard_count = TC_model.objects.filter(
                reporting_period=rp,
                submitted=True,
                user=self.user,
            ).count()
        if timecard_count == 0:
            return True
        else:
            return False

    def save(self, *args, **kwargs):
        """Aligns User model and UserData model attributes on save."""
        user = User.objects.get(username=self.user)
        if self.current_employee:
            user.is_active = True
            user.save()
        else:
            user.is_active = False
            user.is_superuser = False
            user.is_staff = False
            try:
                token = Token.objects.get(user=self.user)
                token.delete()
            except Token.DoesNotExist:
                pass
            user.save()

        super(UserData, self).save(*args, **kwargs)
