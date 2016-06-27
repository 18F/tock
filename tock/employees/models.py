from django.db import models
from django.contrib.auth.models import User

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
