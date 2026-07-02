from common.apps.space.models import Space
from common.apps.upload_file.service import get_presigned_url
from common.celery import constants
from common.celery.task_senders import send_task
from django.conf import settings
from rest_framework import serializers


class SpaceSerializer(serializers.ModelSerializer):
    default_display = serializers.SerializerMethodField()

    class Meta:
        model = Space
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
            "total_devices": {"read_only": True},
            "is_active": {"read_only": True},
            "slug_name": {"read_only": True},
            "is_default": {"read_only": True},
            "created_by": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def validate_slug_name(self, value):
        if value.startswith("default"):
            raise serializers.ValidationError("The slug name is invalid.")
        return value

    def update(self, instance, validated_data):
        old_logo = instance.logo
        new_logo = validated_data.get("logo", old_logo)

        instance = super().update(instance, validated_data)

        if old_logo and old_logo != new_logo:
            send_task(
                name=constants.AUTH_SERVICE_DELETE_UPLOAD_FILE,
                message={
                    "bucket_name": settings.AWS_S3.get("AWS_STORAGE_BUCKET_NAME"),
                    "link_file": f"uploads/{old_logo}",
                },
            )
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.logo:
            data["url_logo"] = get_presigned_url(
                settings.AWS_S3.get("AWS_STORAGE_BUCKET_NAME"),
                f"uploads/{instance.logo}",
            )

        data["created_by"] = getattr(instance, "created_by_display", None)
        data["total_member"] = getattr(instance, "total_member_count", None)

        return data

    def get_default_display(self, obj):
        if hasattr(obj, "default_display"):
            return obj.default_display
        request = self.context.get("request")
        user_id = request.headers.get("X-User-ID", None)
        if not user_id:
            return False
        return obj.space_role.filter(
            space_role_user__organization_user_id=user_id,
            space_role_user__is_default=True,
        ).exists()


class ReceiverSerializer(serializers.Serializer):
    email = serializers.EmailField()
    space_role_id = serializers.UUIDField()


class InviteUserSerial(serializers.Serializer):
    receiver_list = serializers.ListField(child=ReceiverSerializer())
