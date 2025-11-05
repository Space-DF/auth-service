from common.apps.space_role.models import SpaceRole
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from apps.space_role.constants import SpaceRoleType


class IsSpaceAdmin(BasePermission):
    def has_permission(self, request, view):
        user_id = request.headers.get("X-User-ID")
        slug_name = request.headers.get("X-Space")

        if not user_id or not slug_name:
            return False

        has_allowed_role = SpaceRole.objects.filter(
            space_role_user__organization_user__id=user_id,
            space__slug_name=slug_name,
            name=SpaceRoleType.ADMIN_ROLE,
        ).exists()

        if not has_allowed_role:
            raise PermissionDenied("You do not have admin access to this space.")

        return True


class IsSpaceEditor(BasePermission):
    def has_permission(self, request, view):
        user_id = request.headers.get("X-User-ID")
        slug_name = request.headers.get("X-Space")

        if not user_id or not slug_name:
            return False

        has_allowed_role = SpaceRole.objects.filter(
            space_role_user__organization_user__id=user_id,
            space__slug_name=slug_name,
            name__in=[SpaceRoleType.EDITOR_ROLE, SpaceRoleType.ADMIN_ROLE],
        ).exists()

        if not has_allowed_role:
            raise PermissionDenied("You do not have editor access to this space.")
        return True
