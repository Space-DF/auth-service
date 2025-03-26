from common.apps.oauth2.views import GoogleLoginView
from django.urls import include, path

from apps.authentication.views import (
    ChangePasswordAPIView,
    CustomRefreshTokenAPIView,
    LoginAPIView,
    ProfileAPIView,
    RegistrationAPIView,
)

urlpatterns = [
    path("auth/register", RegistrationAPIView.as_view(), name="register"),
    path("auth/login", LoginAPIView.as_view(), name="login"),
    path(
        "auth/change-password", ChangePasswordAPIView.as_view(), name="change_password"
    ),
    path("users/me", ProfileAPIView.as_view(), name="profile"),
    path(
        "auth/refresh-token", CustomRefreshTokenAPIView.as_view(), name="refresh_token"
    ),
    path("auth/spaces/switch", CustomRefreshTokenAPIView.as_view(), name="space_token"),
    path("auth/oauth2/google", GoogleLoginView.as_view(), name="oauth2_google"),
    path("auth/oauth2/", include("apps.spacedf_provider.urls")),
]
