import logging

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import (
    HolidayPrefills, ReportingPeriod, Targets, Timecard, TimecardNote,
    TimecardObject, TimecardPrefillData
)

logger = logging.getLogger('tock-hours')


@receiver(pre_save, sender=HolidayPrefills)
def holiday_prefills_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating HolidayPrefills for {instance}.'
        )


@receiver(pre_save, sender=ReportingPeriod)
def reporting_period_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating ReportingPeriod for {instance}.'
        )


@receiver(pre_save, sender=Targets)
def targets_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating Targets for {instance}.'
        )


@receiver(pre_save, sender=Timecard)
def timecard_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating Timecard for {instance}.'
        )


@receiver(pre_save, sender=TimecardNote)
def timecard_note_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating TimecardNote for {instance}.'
        )


@receiver(pre_save, sender=TimecardObject)
def timecard_object_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating TimecardObject for {instance}.'
        )


@receiver(pre_save, sender=TimecardPrefillData)
def timecard_prefill_data_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating TimecardPrefillData for {instance}.'
        )
