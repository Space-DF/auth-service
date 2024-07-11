from common.apps.organization_user.models import OrganizationUser
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=50, min_length=6)
    password = serializers.CharField(max_length=150, write_only=True)

    class Meta:
        model = OrganizationUser
        fields = ("id", "first_name", "last_name", "email", "password")

    def validate(self, args):
        email = args.get("email", None)
        if OrganizationUser.objects.filter(email__icontains=email).exists():
            raise serializers.ValidationError({"email": "email already exists"})

        return super().validate(args)

    def create(self, validated_data):
        return OrganizationUser.objects.create_user(**validated_data)
