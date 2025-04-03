from common.apps.space.models import Space
from rest_framework import serializers


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


class InviteUserSerial(serializers.Serializer):
    receiver_list = serializers.ListField()
