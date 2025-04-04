from common.apps.space_role.models import SpacePolicy, SpaceRole, SpaceRoleUser
from rest_framework import serializers

from apps.authentication.serializers import ProfileSerializer


class SpacePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = SpacePolicy
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }


class SpaceRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpaceRole
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
            "space": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }


class SpaceRoleUserSerializer(serializers.ModelSerializer):
    space_role = SpaceRoleSerializer(read_only=True)
    organization_user = ProfileSerializer(read_only=True)

    class Meta:
        model = SpaceRoleUser
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }


class SpaceRoleUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpaceRoleUser
        fields = ["space_role"]
