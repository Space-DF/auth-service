from django.urls import path
from space_role.views import (
    ListCreateSpaceRoleView,
    ListPolicyView,
    RetrievePolicyView,
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
        "policies",
        ListPolicyView.as_view(),
    ),
    path(
        "policies/<str:id>",
        RetrievePolicyView.as_view(),
    ),
]
