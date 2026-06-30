from common.apps.organization_user.models import OrganizationUser
from common.apps.upload_file.service import delete_file
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver


@receiver(post_delete, sender=OrganizationUser)
def cleanup_deleted_user_avatar(sender, instance, **kwargs):
    if instance.avatar:
        delete_file(
            settings.AWS_S3.get("AWS_STORAGE_BUCKET_NAME"),
            instance.avatar,
        )
