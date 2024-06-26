from django.urls import path
from organization_role.views import (
    ListCreateOrganizationRoleView,
    ListOrganizationPolicyView,
    ListOrganizationRoleUserView,
    RetrieveDeleteOrganizationRoleUserView,
    RetrieveOrganizationPolicyView,
    UpdateDeleteOrganizationRoleView,
)

app_name = "organization-role"

urlpatterns = [
    path(
        "organization-roles",
        ListCreateOrganizationRoleView.as_view(),
    ),
    path(
        "organization-roles/<str:id>",
        UpdateDeleteOrganizationRoleView.as_view(),
    ),
    path(
        "organization-policies",
        ListOrganizationPolicyView.as_view(),
    ),
    path(
        "organization-policies/<str:id>",
        RetrieveOrganizationPolicyView.as_view(),
    ),
    path(
        "organization-role-users",
        ListOrganizationRoleUserView.as_view(),
    ),
    path(
        "organization-role-users/<str:id>",
        RetrieveDeleteOrganizationRoleUserView.as_view(),
    ),
]
