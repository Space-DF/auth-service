from common.apps.space.models import Space
from common.apps.space_role.models import SpaceRoleUser
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.mqtt_authorize.services import disconnect_user_clients
from apps.space_role.services import (
    clear_user_permission_cache,
    create_space_default_role,
)


@receiver(post_save, sender=SpaceRoleUser)
def handle_post_save(sender, instance, created, **kwargs):
    user_id = getattr(instance, "organization_user_id", None)
    clear_user_permission_cache(user_id)


@receiver(post_delete, sender=SpaceRoleUser)
def handle_post_delete(sender, instance, **kwargs):
    user_id = getattr(instance, "organization_user_id", None)
    clear_user_permission_cache(user_id)
    disconnect_user_clients(user_id)


@receiver(post_save, sender=Space)
@transaction.atomic
def handle_new_space(sender, instance, created, **kwargs):
    if created:
        owner_role, _ = create_space_default_role(instance)
        has_any_space = SpaceRoleUser.objects.filter(
            organization_user_id=instance.created_by
        ).exists()

        SpaceRoleUser.objects.create(
            organization_user_id=instance.created_by,
            space_role=owner_role,
            is_default=not has_any_space,
        )
