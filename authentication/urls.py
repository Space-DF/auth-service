from authentication.views import RegistrationAPIView
from common.apps.oauth2.views import GoogleLoginView
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = "auth"

urlpatterns = [
    path("auth/register", RegistrationAPIView.as_view(), name="register"),
    path("auth/login", TokenObtainPairView.as_view(), name="login"),
    path("auth/refresh-token", TokenRefreshView.as_view(), name="refresh_token"),
    path("auth/oauth2/google", GoogleLoginView.as_view(), name="oauth2_google"),
]
