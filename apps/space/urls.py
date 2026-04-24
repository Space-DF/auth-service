from django.urls import path

from apps.space.views import (
    AddUserToSpaceAPIView,
    GetSpaceUsersAPIView,
    InviteUserAPIView,
    RedirectAddUserToSpaceAPIView,
    SpaceView,
)

app_name = "space"

urlpatterns = [
    path(
        "spaces",
        SpaceView.as_view(),
        name="spaces",
    ),
    path(
        "spaces/<str:space_slug>/users",
        GetSpaceUsersAPIView.as_view(),
        name="get_user_ids",
    ),
    path(
        "spaces/invitation",
        InviteUserAPIView.as_view(),
        name="invitation",
    ),
    path(
        "spaces/join-space/<str:token>",
        AddUserToSpaceAPIView.as_view(),
        name="join_space",
    ),
    path(
        "join-space/<str:token>",
        RedirectAddUserToSpaceAPIView.as_view(),
        name="join_space_redirect",
    ),
]
