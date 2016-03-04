from datetime import date

from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models

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
        return '%s' % (self.user)


def validate_today_or_later(value):
    if value < date.today():
        raise ValidationError(
            'The date provided predates the current date.'
        )


class UserTravelRequest(models.Model):
    requestor_name = models.CharField(
        'Requestor Name',
        blank=False,
        max_length=255
    )
    requestor_email = models.EmailField(
        'Requestor Email',
        blank=False,
        max_length=255
    )
    billability = models.CharField(
        'Billability',
        blank=False,
        choices=(
            ('billable', 'billable'),
            ('non-billable', 'non-billable')
        ),
        max_length=255
    )
    tock_project_name = models.CharField(
        'Project Name',
        blank=False,
        help_text='Exact name of the Tock project',
        max_length=255
    )
    tock_project_id = models.CharField(
        'Project ID',
        blank=False,
        help_text=(
            'Please look up Tock project here: '
            '<a href="https://tock.18f.gov/projects/">https://tock.18f.gov/projects/</a>.'
        ),
        max_length=255
    )
    client_email = models.EmailField(
        'Client Email',
        blank=False,
        help_text='Or supervisor, if non-billable.',
        max_length=255
    )
    home_location = models.CharField(
        'Home Location',
        blank=False,
        help_text='Where you are usually located.',
        max_length=255
    )
    work_location = models.CharField(
        'Work Location',
        blank=False,
        help_text='Where you will be traveling to.',
        max_length=255
    )
    work_to_be_done = models.TextField(
        'Work to be Done',
        blank=False,
        help_text='What you will be working on.',
        max_length=1023
    )
    departure_date = models.DateField(
        'Departure Date',
        blank=False,
        validators=[validate_today_or_later]
    )
    return_date = models.DateField(
        'Return Date',
        blank=False,
        validators=[validate_today_or_later]
    )
    first_day_of_travel_work_date = models.DateField(
        'First Day of Travel Work Date',
        blank=False,
        validators=[validate_today_or_later]
    )
