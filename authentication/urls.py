from authentication.views import RegistrationAPIView
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = "auth"

urlpatterns = [
    path("auth/register", RegistrationAPIView.as_view(), name="register"),
    path("auth/login", TokenObtainPairView.as_view(), name="login"),
    path("auth/refresh-token", TokenRefreshView.as_view(), name="refresh_token"),
]
