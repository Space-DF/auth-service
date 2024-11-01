from common.apps.organization_user.models import OrganizationUser
from common.apps.refresh_tokens.serializers import (
    BaseTokenObtainPairSerializer,
    TokenPairSerializer,
)
from common.errors.errors import ExistedEmailError
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=150, write_only=True, min_length=8)
    default_space = serializers.CharField(read_only=True)

    class Meta:
        model = OrganizationUser
        fields = ("id", "first_name", "last_name", "email", "password", "default_space")

    def validate(self, args):
        email = args.get("email", None)
        if OrganizationUser.objects.filter(email__icontains=email).exists():
            raise ExistedEmailError()

        return super().validate(args)

    def validate_password(self, value: str):
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "This field must contain at least 1 digit."
            )
        if not any(char.isalnum() for char in value):
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

    def create(self, validated_data):
        return OrganizationUser.objects.create_user(**validated_data)


class SpaceDFConsoleLoginSerializer(serializers.Serializer):
    code_verifier = serializers.CharField()
    code = serializers.CharField()
    client_id = serializers.CharField()


class TokenObtainPairSerializer(BaseTokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        default_space = self.user.created_space.first()
        data["default_space"] = default_space.slug_name if default_space else None

        return data


class AuthTokenPairSerializer(TokenPairSerializer):
    default_space = serializers.CharField()
