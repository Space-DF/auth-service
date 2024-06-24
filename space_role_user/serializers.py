from rest_framework import serializers
from space_role_user.models import SpaceRoleUser


class SpaceRoleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpaceRoleUser
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }
