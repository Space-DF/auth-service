from common.apps.space.models import Space
from django.conf import settings
from rest_framework import serializers

from apps.upload_file.service import get_url


class SpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
            "total_devices": {"read_only": True},
            "is_active": {"read_only": True},
            "created_by": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def validate_slug_name(self, value):
        if value.startswith("default"):
            raise serializers.ValidationError("The slug name is invalid.")
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.logo:
            data["logo"] = get_url(
                settings.AWS_S3.get("AWS_STORAGE_BUCKET_NAME"),
                settings.AWS_S3.get("AWS_REGION"),
                instance.logo,
            )
        return data


class ReceiverSerializer(serializers.Serializer):
    email = serializers.EmailField()
    space_role_id = serializers.UUIDField()


class InviteUserSerial(serializers.Serializer):
    receiver_list = serializers.ListField(child=ReceiverSerializer())
