from django.urls import path

from apps.oauth_credentials.views import RetriveOauthCredentialsView

app_name = "oauth-redentials"

urlpatterns = [
    path(
        "credentials",
        RetriveOauthCredentialsView.as_view(),
    )
]
