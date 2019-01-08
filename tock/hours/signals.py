import logging

from django.db.models.signals import pre_save

logger = logging.getLogger('tock-hours')


def holiday_prefills_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating HolidayPrefills for {instance}.'
        )


def reporting_period_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating ReportingPeriod for {instance}.'
        )


def timecard_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating Timecard for {instance}.'
        )


def timecard_note_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating TimecardNote for {instance}.'
        )


def timecard_object_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating TimecardObject for {instance}.'
        )


def timecard_prefill_data_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating TimecardPrefillData for {instance}.'
        )


def setup_signals():
    from .models import (
        HolidayPrefills, ReportingPeriod, Timecard, TimecardNote,
        TimecardObject, TimecardPrefillData
    )

    pre_save.connect(
        holiday_prefills_creation,
        sender=HolidayPrefills,
        dispatch_uid="hours_holiday_prefills_creation"
    )
    pre_save.connect(
        reporting_period_creation,
        sender=ReportingPeriod,
        dispatch_uid="hours_reporting_period_creation"
    )
    pre_save.connect(
        timecard_creation,
        sender=Timecard,
        dispatch_uid="hours_timecard_creation"
    )
    pre_save.connect(
        timecard_note_creation,
        sender=TimecardNote,
        dispatch_uid="hours_timecard_note_creation"
    )
    pre_save.connect(
        timecard_object_creation,
        sender=TimecardObject,
        dispatch_uid="hours_timecard_object_creation"
    )
    pre_save.connect(
        timecard_prefill_data_creation,
        sender=TimecardPrefillData,
        dispatch_uid="hours_timecard_prefill_data_creation"
    )
