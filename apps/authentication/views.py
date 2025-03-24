from common.apps.organization_user.models import OrganizationUser
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.authentication.serializers import (
    AuthTokenPairSerializer,
    ChangePasswordSerializer,
    ProfileSerializer,
    RegistrationSerializer,
)
from apps.authentication.services import (
    create_space_access_token,
    create_space_jwt_tokens,
)


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
    authentication_classes = []
    _serializer_class = "apps.authentication.serializers.SpaceTokenRefreshSerializer"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        space_slug = self.request.data.get("space")
        params = {
            "space_slug_name": space_slug,
        }
        return {
            **context,
            "access_token_handler": create_space_access_token,
            "access_token_handler_params": params,
        }


class LoginAPIView(TokenObtainPairView):
    authentication_classes = []

    @swagger_auto_schema(
        responses={status.HTTP_201_CREATED: AuthTokenPairSerializer},
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        return super().post(request, *args, **kwargs)


class ChangePasswordAPIView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        user_id = self.request.headers.get("X-User-ID", None)
        if not user_id:
            return None
        return get_object_or_404(OrganizationUser, id=user_id)

    def put(self, request: Request):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileAPIView(generics.RetrieveAPIView):
    queryset = OrganizationUser.objects.all()
    serializer_class = ProfileSerializer

    def get_object(self):
        user_id = self.request.headers.get("X-User-ID", None)
        if not user_id:
            raise NotFound(detail="The user not found")
        return get_object_or_404(OrganizationUser, id=user_id)

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: ProfileSerializer()},
    )
    def get(self, request: Request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=ProfileSerializer,
        responses={status.HTTP_200_OK: ProfileSerializer()},
    )
    def put(self, request: Request):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
