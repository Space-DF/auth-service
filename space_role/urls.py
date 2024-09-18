from django.urls import path

from space_role.views import (
    ListCreateSpaceRoleView,
    ListSpacePolicyView,
    ListSpaceRoleUserView,
    RetrieveDeleteSpaceRoleUserView,
    RetrieveSpacePolicyView,
    UpdateDeleteSpaceRoleView,
)

app_name = "space-role"

urlpatterns = [
    path(
        "space-roles",
        ListCreateSpaceRoleView.as_view(),
    ),
    path(
        "space-roles/<str:id>",
        UpdateDeleteSpaceRoleView.as_view(),
    ),
    path(
        "space-policies",
        ListSpacePolicyView.as_view(),
    ),
    path(
        "space-policies/<str:id>",
        RetrieveSpacePolicyView.as_view(),
    ),
    path(
        "space-role-users",
        ListSpaceRoleUserView.as_view(),
    ),
    path(
        "space-role-users/<str:id>",
        RetrieveDeleteSpaceRoleUserView.as_view(),
    ),
]
