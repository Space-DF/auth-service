from allauth.socialaccount.models import SocialApp
from common.permissions.permission_classes import HasRootAPIKey
from drf_yasg.utils import swagger_auto_schema
from rest_framework import renderers, status
from rest_framework.generics import RetrieveAPIView

from oauth_credentials.serializers import OAuthCredentialsSerializer


class RetriveOauthCredentialsView(RetrieveAPIView):
    serializer_class = OAuthCredentialsSerializer
    queryset = SocialApp.objects.all()
    permission_classes = [HasRootAPIKey]
    renderer_classes = [renderers.JSONRenderer]

    def get_object(self):
        with self.request.tenant:
            return self.queryset.first()

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: OAuthCredentialsSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
