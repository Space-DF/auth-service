from common.apps.organization_user.models import OrganizationUser
from common.apps.space.models import Space
from common.apps.space_role.models import SpaceRoleUser
from django.conf import settings
from django.db.models import Case, CharField, Count, F, OuterRef, Value, When
from django.db.models.functions import Coalesce, Concat, Length, Trim
from rest_framework import serializers

from apps.upload_file.service import get_url


class SpaceSerializer(serializers.ModelSerializer):
    default_display = serializers.SerializerMethodField()

    class Meta:
        model = Space
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
            "total_devices": {"read_only": True},
            "is_active": {"read_only": True},
            "is_default": {"read_only": True},
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

        created_by = (
            OrganizationUser.objects.filter(id=instance.created_by)
            .annotate(
                full_name=Concat(
                    Coalesce(F("first_name"), Value("")),
                    Value(" "),
                    Coalesce(F("last_name"), Value("")),
                    output_field=CharField(),
                )
            )
            .annotate(full_len=Length(Trim(F("full_name"))))
            .annotate(
                value=Case(
                    When(full_len__gt=0, then=F("full_name")),
                    default=Concat(Value(""), F("email"), output_field=CharField()),
                    output_field=CharField(),
                )
            )
            .values_list("value", flat=True)
            .first()
        )
        data["created_by"] = created_by

        total_member = SpaceRoleUser.objects.filter(
            space_role__space=instance.pk
        ).aggregate(count=Count("organization_user", distinct=True))["count"]
        data["total_member"] = total_member

        return data

    def get_default_display(self, obj):
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
