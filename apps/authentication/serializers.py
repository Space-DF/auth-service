from common.apps.organization_user.models import OrganizationUser
from common.apps.refresh_tokens.serializers import (
    BaseTokenObtainPairSerializer,
    CustomTokenRefreshSerializer,
    TokenPairSerializer,
)
from common.apps.space.models import Space
from common.apps.upload_file.service import get_presigned_url
from common.errors.errors import ExistedEmailError
from django.conf import settings
from django.core.cache import cache
from rest_framework import serializers

from apps.authentication.services import create_space_jwt_tokens


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=150, write_only=True, min_length=8)
    default_space = serializers.CharField(read_only=True)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    otp = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = OrganizationUser
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "password",
            "default_space",
            "otp",
        )

    def validate(self, data):
        email = data.get("email", None)
        if OrganizationUser.objects.filter(email__icontains=email).exists():
            raise ExistedEmailError()
        otp = data.get("otp")
        stored_otp = cache.get(f"otp_{email}")
        if not stored_otp or stored_otp != otp:
            raise serializers.ValidationError({"otp": "Invalid or expired OTP."})
        return super().validate(data)

    def validate_password(self, value: str):
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "This field must contain at least 1 digit."
            )
        if all(char.isalnum() for char in value):
            raise serializers.ValidationError(
                "This field must contain at least 1 special letter"
            )
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(
                "This field must contain at least 1 upper case letter"
            )
        if not any(char.islower() for char in value):
            raise serializers.ValidationError(
                "This field must contain at least 1 lower case letter"
            )
        return value

    def validate_first_name(self, value: str):
        if not all(char.isalnum() for char in value):
            raise serializers.ValidationError(
                "This field must not contain any special letter"
            )
        return value.strip()

    def validate_last_name(self, value: str):
        if not all(char.isalnum() for char in value):
            raise serializers.ValidationError(
                "This field must not contain any special letter"
            )
        return value.strip()

    def create(self, validated_data):
        email = validated_data.get("email")
        validated_data.pop("otp", None)  # Ensure OTP is not passed to the database
        cache.delete(
            f"otp_{email}"
        )  # Remove OTP from Redis after successful validation
        return OrganizationUser.objects.create_user(**validated_data)


class SpaceDFConsoleLoginSerializer(serializers.Serializer):
    code_verifier = serializers.CharField()
    code = serializers.CharField()
    client_id = serializers.CharField()


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    avatar = serializers.CharField(required=False)
    is_owner = serializers.BooleanField(read_only=True)
    is_set_password = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationUser
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "location",
            "avatar",
            "company_name",
            "title",
            "is_owner",
            "is_set_password",
        )

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.avatar:
            data["avatar"] = get_presigned_url(
                settings.AWS_S3.get("AWS_STORAGE_BUCKET_NAME"),
                f"uploads/{instance.avatar}.png",
            )
        return data

    def get_is_set_password(self, instance):
        return instance.has_usable_password()


class TokenObtainPairSerializer(BaseTokenObtainPairSerializer):
    def get_tokens(self):
        tenant = None
        if hasattr(self.context["request"], "tenant"):
            tenant = self.context["request"].tenant

        default_space = Space.objects.filter(
            space_role__space_role_user__organization_user_id=self.user.id,
            space_role__space_role_user__is_default=True,
        ).first()
        default_space_slug = default_space.slug_name if default_space else None
        refresh_token, access_token = create_space_jwt_tokens(
            self.user, space_slug=default_space_slug, issuer=tenant
        )

        return refresh_token, access_token, default_space_slug

    def get_response_data(self):
        refresh_token, access_token, default_space = self.get_tokens()

        return {
            "refresh": str(refresh_token),
            "access": str(access_token),
            "default_space": default_space,
        }


class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, write_only=True
    )
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value: str):
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "This new password must contain at least 1 digit."
            )
        if all(char.isalnum() for char in value):
            raise serializers.ValidationError(
                "This new password must contain at least 1 special letter"
            )
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(
                "This new password must contain at least 1 upper case letter"
            )
        if not any(char.islower() for char in value):
            raise serializers.ValidationError(
                "This new password must contain at least 1 lower case letter"
            )
        return value

    def update(self, instance, validated_data):
        current_password = validated_data.get("password")
        new_password = validated_data.get("new_password")

        if instance.has_usable_password():
            if not current_password:
                raise serializers.ValidationError(
                    {"password": "Current password is required."}
                )
            if not instance.check_password(current_password):
                raise serializers.ValidationError(
                    {"error": "Current password is incorrect"}
                )
            if current_password == new_password:
                raise serializers.ValidationError(
                    {"error": "New password cannot be the same as the current password"}
                )

        instance.set_password(new_password)
        instance.save()
        return instance


class AuthTokenPairSerializer(TokenPairSerializer):
    default_space = serializers.CharField()


class SendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class SpaceTokenRefreshSerializer(CustomTokenRefreshSerializer):
    space_slug_name = serializers.CharField(write_only=True, allow_null=True)


class ForgetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField()
