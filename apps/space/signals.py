from common.apps.organization_user.models import OrganizationUser
from common.apps.space.models import Space
from common.apps.upload_file.service import delete_file
from common.celery import constants
from common.celery.task_senders import send_task
from django.conf import settings
from django.db import connection
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver

from apps.space_role.services import clear_user_permission_cache


@receiver(post_save, sender=Space)
def handle_device_space_create(sender, instance, created, **kwargs):
    if not created:
        return

    tenant = connection.get_tenant()
    slug_name = getattr(tenant, "slug_name", connection.schema_name)

    send_task(
        name=constants.CONSOLE_SERVICE_ADD_OR_REMOVE_SPACE,
        message={
            "slug_name": slug_name,
            "type": "add",
        },
    )


@receiver(post_save, sender=OrganizationUser)
def create_default_space(sender, instance, created, **kwargs):
    if created:
        Space(
            name="Default",
            slug_name=f"default-{instance.id}",
            created_by=instance.id,
            is_default=True,
        ).save()


@receiver(post_delete, sender=Space)
def handle_post_delete(sender, instance, **kwargs):
    if instance.logo:
        delete_file(
            settings.AWS_S3.get("AWS_STORAGE_BUCKET_NAME"),
            instance.logo,
        )

    # Clear permission cache for all users associated with the space
    user_id = getattr(instance, "created_by", None)
    clear_user_permission_cache(user_id)


@receiver(pre_delete, sender=Space)
def handle_device_space_delete(sender, instance, **kwargs):
    tenant = connection.get_tenant()
    slug_name = getattr(tenant, "slug_name", connection.schema_name)

    send_task(
        name=constants.CONSOLE_SERVICE_ADD_OR_REMOVE_SPACE,
        message={
            "slug_name": slug_name,
            "type": "remove",
        },
    )
