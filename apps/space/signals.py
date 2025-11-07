from common.apps.organization_user.models import OrganizationUser
from common.apps.space.models import Space
from common.celery import constants
from common.celery.task_senders import send_task
from django.db import connection
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver


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
