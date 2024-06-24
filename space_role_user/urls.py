from django.urls import path
from space_role_user.views import ListSpaceRoleUserView, RetrieveDeleteSpaceRoleUserView

app_name = "space-role-user"

urlpatterns = [
    path(
        "space-role-users",
        ListSpaceRoleUserView.as_view(),
    ),
    path(
        "space-role-users/<str:id>",
        RetrieveDeleteSpaceRoleUserView.as_view(),
    ),
]
