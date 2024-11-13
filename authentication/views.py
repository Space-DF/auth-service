from common.permissions.permission_classes import HasSpaceName
from common.swagger.params import get_space_header_params
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from authentication.serializers import AuthTokenPairSerializer, RegistrationSerializer
from authentication.services import create_space_access_token, create_space_jwt_tokens


class RegistrationAPIView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            default_space_slug = f"default-{user.id}"
            refresh_token, access_token = create_space_jwt_tokens(
                user, space_slug=default_space_slug, issuer=request.tenant
            )
            return Response(
                {
                    "message": "User created successfully",
                    "user": serializer.data,
                    "refresh": str(refresh_token),
                    "access": str(access_token),
                    "default_space": default_space_slug,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomRefreshTokenAPIView(TokenRefreshView):
    authentication_classes = [HasSpaceName]

    @swagger_auto_schema(manual_parameters=get_space_header_params())
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        return {**context, "access_token_handler": create_space_access_token}


class LoginAPIView(TokenObtainPairView):
    authentication_classes = []

    @swagger_auto_schema(
        responses={status.HTTP_201_CREATED: AuthTokenPairSerializer},
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        return super().post(request, *args, **kwargs)
