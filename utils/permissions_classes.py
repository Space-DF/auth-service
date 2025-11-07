from common.apps.space_role.constants import SpaceRoleType
from common.apps.space_role.models import SpaceRole
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


class BaseSpacePermission(BasePermission):
    allowed_roles = []
    error_message = "You do not have permission to access this space."

    def has_permission(self, request, view):
        user_id = request.headers.get("X-User-ID")
        slug_name = request.headers.get("X-Space")

        if not user_id or not slug_name:
            return False

        has_allowed_role = SpaceRole.objects.filter(
            space_role_user__organization_user__id=user_id,
            space__slug_name=slug_name,
            name__in=self.allowed_roles,
        ).exists()

        print("okiu", has_allowed_role)

        if not has_allowed_role:
            raise PermissionDenied(self.error_message)
        return True


class IsSpaceAdmin(BaseSpacePermission):
    allowed_roles = [SpaceRoleType.ADMIN_ROLE]
    error_message = "You do not have admin access to this space."


class IsSpaceEditor(BaseSpacePermission):
    allowed_roles = [SpaceRoleType.EDITOR_ROLE, SpaceRoleType.ADMIN_ROLE]
    error_message = "You do not have editor access to this space."
