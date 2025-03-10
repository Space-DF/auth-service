from django.urls import path

from apps.space.views import SpaceView

app_name = "space"

urlpatterns = [
    path(
        "spaces",
        SpaceView.as_view(),
    ),
]
