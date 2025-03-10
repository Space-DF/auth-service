from common.apps.organization_user.models import OrganizationUser
from common.apps.refresh_tokens.serializers import (
    BaseTokenObtainPairSerializer,
    TokenPairSerializer,
)
from common.apps.space.models import Space
from common.errors.errors import ExistedEmailError
from rest_framework import serializers

from apps.authentication.services import create_space_jwt_tokens


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=150, write_only=True, min_length=8)
    default_space = serializers.CharField(read_only=True)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)

    class Meta:
        model = OrganizationUser
        fields = ("id", "first_name", "last_name", "email", "password", "default_space")

    def validate(self, data):
        email = data.get("email", None)
        if OrganizationUser.objects.filter(email__icontains=email).exists():
            raise ExistedEmailError()
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
        return OrganizationUser.objects.create_user(**validated_data)


class SpaceDFConsoleLoginSerializer(serializers.Serializer):
    code_verifier = serializers.CharField()
    code = serializers.CharField()
    client_id = serializers.CharField()


class TokenObtainPairSerializer(BaseTokenObtainPairSerializer):
    def get_tokens(self):
        tenant = None
        if hasattr(self.context["request"], "tenant"):
            tenant = self.context["request"].tenant

        default_space = Space.objects.filter(created_by=self.user.id).first()
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


class AuthTokenPairSerializer(TokenPairSerializer):
    default_space = serializers.CharField()
