from common.apps.billing.constants import FeatureCode, FeatureUsageScope
from common.apps.organization_user.models import OrganizationUser
from common.apps.space.models import Space
from common.apps.upload_file.service import delete_file
from common.celery import constants
from common.celery.task_senders import send_task
from common.utils.console_client import console_client
from django.conf import settings
from django.db import connection
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver

from apps.space_role.services import clear_user_permission_cache


def _get_org_slug():
    tenant = connection.get_tenant()
    return getattr(tenant, "slug_name", connection.schema_name)


@receiver(post_save, sender=Space)
def handle_device_space_create(sender, instance, created, **kwargs):
    if not created:
        return

    send_task(
        name=constants.CONSOLE_SERVICE_ADD_OR_REMOVE_SPACE,
        message={
            "slug_name": _get_org_slug(),
            "type": "add",
        },
    )


@receiver(post_save, sender=OrganizationUser)
def create_default_space(sender, instance, created, **kwargs):
    if not created:
        return

    org_slug = _get_org_slug()
    reserved, error = console_client.reserve_quota(
        org_slug,
        FeatureCode.SPACE_MAX_COUNT,
        scope_type=FeatureUsageScope.USER,
        scope_id=instance.id,
    )
    if not reserved:
        raise RuntimeError(error or "Unable to reserve quota for default space.")

    try:
        Space(
            name="Default",
            slug_name=f"default-{instance.id}",
            created_by=instance.id,
            is_default=True,
        ).save()
    except Exception:
        console_client.release_quota(
            org_slug,
            FeatureCode.SPACE_MAX_COUNT,
            scope_type=FeatureUsageScope.USER,
            scope_id=instance.id,
        )
        raise


@receiver(post_delete, sender=Space)
def handle_post_delete(sender, instance, **kwargs):
    if instance.logo:
        delete_file(
            settings.AWS_S3.get("AWS_STORAGE_BUCKET_NAME"),
            f"uploads/{instance.logo}",
        )

    # Clear permission cache for all users associated with the space
    user_id = getattr(instance, "created_by", None)
    clear_user_permission_cache(user_id)


@receiver(pre_delete, sender=Space)
def handle_device_space_delete(sender, instance, **kwargs):
    send_task(
        name=constants.CONSOLE_SERVICE_ADD_OR_REMOVE_SPACE,
        message={
            "slug_name": _get_org_slug(),
            "type": "remove",
        },
    )
