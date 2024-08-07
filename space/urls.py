from django.urls import path
from space.views import SpaceView

app_name = "space"

urlpatterns = [
    path(
        "spaces",
        SpaceView.as_view(),
    ),
]
