import logging

from django.db.models.signals import pre_save

logger = logging.getLogger('tock-projects')


def agency_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating Agency for {instance}.'
        )

def accounting_code_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating AccountingCode for {instance}.'
        )


def project_alert_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating ProjectAlert for {instance}.'
        )


def profit_loss_account_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating ProfitLossAccount for {instance}.'
        )


def project_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating Project for {instance}.'
        )

def setup_signals():
    from .models import (
        Agency, AccountingCode, ProjectAlert, ProfitLossAccount, Project
    )

    pre_save.connect(
        agency_creation,
        sender=Agency,
        dispatch_uid="project_agency_creation"
    )
    pre_save.connect(
        accounting_code_creation,
        sender=AccountingCode,
        dispatch_uid="project_accounting_code_creation"
    )
    pre_save.connect(
        project_alert_creation,
        sender=ProjectAlert,
        dispatch_uid="project_project_alert_creation"
    )
    pre_save.connect(
        project_creation,
        sender=Project,
        dispatch_uid="project_project_creation"
    )
