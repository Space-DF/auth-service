import logging

import requests
from allauth.socialaccount.models import EmailAddress, SocialApp
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter
from common.apps.refresh_tokens.services import create_refresh_token
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from requests import HTTPError
from rest_framework import generics, permissions, response, status
from rest_framework.exceptions import ParseError

from authentication.serializers import SpaceDFConsoleLoginSerializer

logger = logging.getLogger(__name__)

SPACE_DF_TOKEN_URL = f"{settings.CONSOLE_SERVICE_URL}/oauth2/token"
User = get_user_model()


class SpaceDFAdapter(OAuth2Adapter):
    provider_id = "spacedf"
    access_token_url = SPACE_DF_TOKEN_URL

    def complete_login(self, request, app, token, **kwargs):
        if not token:
            raise ValueError("ID token not found in the token response")

        provider = self.get_provider()
        try:
            user_data = provider.decode_id_token(token)
            return self.get_provider().sociallogin_from_response(request, user_data)
        except ValueError as e:
            logger.exception(e)
            raise ParseError

    def get_token(self, app, validated_data):
        data = {**validated_data, "client_secret": app.secret}
        try:
            response = requests.post(self.access_token_url, data=data)  # nosec
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            logger.exception(e)
            raise ParseError(detail="Invalid credentials")

    def get_user_data(self, login):
        return login.account.extra_data.get("user", {})

    def get_user_email(self, login):
        return self.get_user_data(login).get("email", "")

    def save_user(self, request, sociallogin, form=None):
        email = self.get_user_email(sociallogin)
        existing_user = None
        if email:
            try:
                existing_user = User.objects.get(email=email)
            except EmailAddress.DoesNotExist:
                pass

        if existing_user:
            try:
                sociallogin.connect(request, existing_user)
            except IntegrityError:
                pass
            user = existing_user
        else:
            sociallogin.save(request)
            user = sociallogin.account.user
        return user


class SpaceDFConsoleLoginView(generics.GenericAPIView):
    serializer_class = SpaceDFConsoleLoginSerializer
    permission_classes = [permissions.AllowAny]

    def dispatch(self, request, *args, **kwargs):
        self.adapter = SpaceDFAdapter(request)
        self.app = SocialApp.objects.get(provider_id=SpaceDFAdapter.provider_id)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        token = self.adapter.get_token(self.app, validated_data).get("id_token", "")
        login = self.adapter.complete_login(request, app=self.app, token=token)

        user = self.adapter.save_user(request, login)

        refresh, access = create_refresh_token(user, issuer=request.tenant)

        return response.Response(
            {"refresh": str(refresh), "access": str(access)},
            status=status.HTTP_201_CREATED,
        )
