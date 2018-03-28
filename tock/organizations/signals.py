import logging

from django.db.models.signals import pre_save

logger = logging.getLogger('tock-organizations')


def organization_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating Organization for {instance}.'
        )


def setup_signals():
    from .models import Organization

    pre_save.connect(
        organization_creation,
        sender=Organization,
        dispatch_uid="organizations_organization_creation"
    )
