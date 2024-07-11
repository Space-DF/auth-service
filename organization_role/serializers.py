from common.apps.organization_role.models import (
    OrganizationPolicy,
    OrganizationRole,
    OrganizationRoleUser,
)
from rest_framework import serializers


class OrganizationPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationPolicy
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }


class OrganizationRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationRole
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }


class OrganizationRoleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationRoleUser
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }
