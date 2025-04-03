from django.urls import path

from apps.space.views import AddUserToSpaceAPIView, InviteUserAPIView, SpaceView

app_name = "space"

urlpatterns = [
    path(
        "spaces",
        SpaceView.as_view(),
    ),
    path("invitation/<str:space_id>", InviteUserAPIView.as_view(), name="invitation"),
    path("join-space/<str:token>", AddUserToSpaceAPIView.as_view(), name="join_space"),
]
