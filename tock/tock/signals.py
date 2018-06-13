import logging

from django.contrib.auth.signals import user_logged_in, user_logged_out, \
    user_login_failed
from django.db.models.signals import post_save, m2m_changed

logger = logging.getLogger('tock')


def successful_login(sender, request, user, **kwargs):
    logger.info(f'Successful login event for {user.username}.')


def successful_logout(sender, request, user, **kwargs):
    logger.info(f'Successful logout event for {user}.')


def failed_login(sender, credentials, request, **kwargs):
    logger.info(f'Unsuccessful login attempt by {credentials}.')


def adminlog_post_save(sender, instance, **kwargs):
    from django.contrib.admin.models import ADDITION, CHANGE, DELETION
    if instance.action_flag == ADDITION:
        logger.info(
            f'[admin-log] {instance.user} created {instance.content_type} {instance.object_repr} @ {instance.get_admin_url()}.'
        )
    elif instance.action_flag == CHANGE:
        logger.info(
            f'[admin-log] {instance.user} changed {instance.content_type} {instance.object_repr}: '
            f'{instance.change_message} @ {instance.get_admin_url()}.'
        )
    elif instance.action_flag == DELETION:
        logger.info(
            f'[admin-log] {instance.user} deleted {instance.content_type} {instance.object_repr} @ {instance.get_admin_url()}.'
        )

def log_m2m_change(sender, instance, action, reverse, model, pk_set, **kwargs):
    model_name = model._meta.verbose_name_plural
    instance_model = instance._meta.verbose_name
    if action == 'post_add':
        objects_added = list(model.objects.filter(pk__in=pk_set))
        logger.info(
            f'[account-management] {model_name} given to {instance_model} {instance}: {objects_added}.'
        )
    elif action == 'post_remove':
        objects_added = list(model.objects.filter(pk__in=pk_set))
        logger.info(
            f'[account-management] {model_name} removed from {instance_model} {instance}: {objects_added}.'
        )
        logger.info("%s removed from %s '%s': %s", model_name, instance_model,
                    instance, objects_added)
    elif action == 'post_clear':
        logger.info(
            f'[account-management] All {model_name} removed from {instance_model} {instance}.'
        )

def setup_signals():
    from django.contrib.auth.models import User, Group
    from django.contrib.admin.models import LogEntry

    user_logged_in.connect(
        successful_login,
        dispatch_uid="tock_successful_login"
    )
    user_logged_out.connect(
        successful_logout,
        dispatch_uid="tock_successful_logout"
    )
    user_login_failed.connect(
        failed_login,
        dispatch_uid="tock_failed_login"
    )
    post_save.connect(
        adminlog_post_save,
        sender=LogEntry,
        dispatch_uid="tock_adminlog_post_save"
    )
    m2m_changed.connect(
        log_m2m_change,
        sender=User.groups.through,
        dispatch_uid="tock_log_m2m_changed_user_groups"
    )
    m2m_changed.connect(
        log_m2m_change,
        sender=User.user_permissions.through,
        dispatch_uid="tock_log_m2m_changed_user_permissions"
    )
    m2m_changed.connect(
        log_m2m_change,
        sender=Group.permissions.through,
        dispatch_uid="tock_log_m2m_changed_groups_permissions"
    )
