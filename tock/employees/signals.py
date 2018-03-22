import logging

from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import EmployeeGrade, UserData

logger = logging.getLogger('tock-employees')


@receiver(pre_save, sender=EmployeeGrade)
def employee_grade_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating EmployeeGrade for {instance.employee.username}.'
        )

@receiver(pre_save, sender=UserData)
def user_data_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating UserData for {instance.user.username}.'
        )
