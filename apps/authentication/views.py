from datetime import datetime, timezone

from common.apps.oauth2.serializers import CodeLoginSerializer
from common.apps.organization_user.models import OrganizationUser
from common.permissions.permission_classes import HasChangePermission
from common.utils.oauth2 import get_access_token_with_code
from common.utils.send_email import send_email
from common.utils.token_jwt import generate_token
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.authentication.serializers import (
    AuthTokenPairSerializer,
    ChangePasswordSerializer,
    ForgetPasswordSerializer,
    ProfileSerializer,
    RegistrationSerializer,
    SendEmailSerializer,
)
from apps.authentication.services import (
    create_space_access_token,
    create_space_jwt_tokens,
    generate_otp,
    handle_space_access_token,
    render_email_format,
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
    _serializer_class = "apps.authentication.serializers.CustomTokenRefreshSerializer"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        params = {}
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


class GoogleLoginTokenView(generics.CreateAPIView):
    serializer_class = CodeLoginSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        authorization_code = serializer.validated_data["authorization_code"]
        access_token = get_access_token_with_code(authorization_code, provider="GOOGLE")
        return handle_space_access_token(
            request, access_token=access_token, provider="GOOGLE"
        )


class SendOTPView(generics.GenericAPIView):
    """API View to send OTP for email verification"""

    serializer_class = SendEmailSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            otp_code = generate_otp()
            email = serializer.validated_data["email"]
            subject = "Your One-Time Sign-In Code"
            data = {
                "otp_code": otp_code,
            }
            message = render_email_format("email_otp.html", data)
            send_email(settings.DEFAULT_FROM_EMAIL, [email], subject, message)
            cache.set(f"otp_{email}", otp_code, timeout=600)
            return Response({"message": "OTP sent successfully!"})

        return Response(serializer.errors, status=400)


class SendEmailToConfirmView(generics.GenericAPIView):
    serializer_class = SendEmailSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        subject = "Forget the password"
        token = generate_token({"email": email})
        data = {
            "token": token,
            "slug_name": request.tenant.slug_name + ".",
        }
        message = render_email_format("email_forget_password.html", data)
        send_email(settings.DEFAULT_FROM_EMAIL, [email], subject, message)
        return Response(
            {
                "result": "Please check your email to continue the password reset process"
            },
            status=status.HTTP_200_OK,
        )


class ForgetPasswordView(generics.GenericAPIView):
    serializer_class = ForgetPasswordSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_str = serializer.validated_data["token"]
        if cache.get(f"used_token:{token_str}"):
            return Response(
                {"error": "This token has already been used"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = AccessToken(token_str)
            orgianization_user = OrganizationUser.objects.filter(
                email=token.get("email")
            ).first()
            if orgianization_user:
                orgianization_user.set_password(serializer.validated_data["password"])
                orgianization_user.save()

                exp_timestamp = token.get("exp")
                exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
                ttl_seconds = int((exp_datetime - token.current_time).total_seconds())
                cache.set(f"used_token:{token_str}", True, timeout=ttl_seconds)

                return Response(
                    {"result": "The password changed successfully"},
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"result": "The account for this email does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"Invalid or expired token.{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ChangePasswordAPIView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [HasChangePermission]

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
    permission_classes = [HasChangePermission]

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

    def delete(self, request: Request):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
