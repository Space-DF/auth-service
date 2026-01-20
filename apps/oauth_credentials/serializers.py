from allauth.socialaccount.models import SocialApp
from rest_framework import serializers


class OAuthCredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialApp
        fields = ["client_id"]
