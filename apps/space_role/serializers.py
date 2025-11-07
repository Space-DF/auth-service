from common.apps.space_role.constants import SpaceRoleType
from common.apps.space_role.models import SpacePolicy, SpaceRole, SpaceRoleUser
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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

    def validate(self, data):
        instance = self.instance
        new_role = data.get("space_role", None)

        if not new_role:
            return data

        if (
            instance.space_role.name == SpaceRoleType.ADMIN_ROLE
            and new_role.name != SpaceRoleType.ADMIN_ROLE
            and not SpaceRoleUser.objects.filter(
                space_role__space=instance.space_role.space,
                space_role__name__iexact=SpaceRoleType.ADMIN_ROLE,
            )
            .exclude(id=instance.id)
            .exists()
        ):
            raise ValidationError(
                {"detail": "Cannot demote the last admin in this space"}
            )

        return data
