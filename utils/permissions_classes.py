from common.apps.space_role.models import SpaceRole
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


class IsSpaceAdmin(BasePermission):
    def has_permission(self, request, view):
        user_id = request.headers.get("X-User-ID")
        slug_name = request.headers.get("X-Space")

        if not user_id or not slug_name:
            return False

        is_space_admin = SpaceRole.objects.filter(
            space_role_user__organization_user__id=user_id,
            space__slug_name=slug_name,
            name="Admin",
        ).exists()

        if not is_space_admin:
            raise PermissionDenied("You do not have admin access to this space.")

        return True
