import logging

from django.db.models.signals import pre_save
from django.dispatch import receiver

logger = logging.getLogger('tock-employees')


def employee_grade_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating EmployeeGrade for {instance.employee.username}.'
        )

def user_data_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating UserData for {instance.user.username}.'
        )


def setup_signals():
    from .models import EmployeeGrade, UserData

    pre_save.connect(
        employee_grade_creation,
        sender=EmployeeGrade,
        dispatch_uid="employees_employee_grade_creation"
    )
    pre_save.connect(
        user_data_creation,
        sender=UserData,
        dispatch_uid="employees_user_data_creation"
    )
