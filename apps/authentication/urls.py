from common.apps.oauth2.views import GoogleLoginTokenView, GoogleLoginView
from django.urls import include, path

from apps.authentication.views import (
    ChangePasswordAPIView,
    CustomRefreshTokenAPIView,
    ForgetPasswordView,
    LoginAPIView,
    ProfileAPIView,
    RegistrationAPIView,
    SendEmailToConfirmView,
    SendOTPView,
)

urlpatterns = [
    path("auth/register", RegistrationAPIView.as_view(), name="register"),
    path("auth/login", LoginAPIView.as_view(), name="login"),
    path(
        "auth/change-password", ChangePasswordAPIView.as_view(), name="change_password"
    ),
    path("auth/forget-password", ForgetPasswordView.as_view(), name="forget_password"),
    path("auth/google/login", GoogleLoginTokenView.as_view(), name="google-callback"),
    path("users/me", ProfileAPIView.as_view(), name="profile"),
    path(
        "auth/refresh-token", CustomRefreshTokenAPIView.as_view(), name="refresh_token"
    ),
    path("auth/spaces/switch", CustomRefreshTokenAPIView.as_view(), name="space_token"),
    path("auth/oauth2/google", GoogleLoginView.as_view(), name="oauth2_google"),
    path("auth/oauth2/", include("apps.spacedf_provider.urls")),
    path("auth/send-otp", SendOTPView.as_view(), name="send_otp"),
    path(
        "auth/send-email-confirm", SendEmailToConfirmView.as_view(), name="send_email"
    ),
]
