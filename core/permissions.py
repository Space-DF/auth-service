from rest_framework.exceptions import ParseError
from rest_framework.permissions import BasePermission
from space_role.models import Policy


def has_permission_access(permission):
    """
    Allows access only to users who have specific permissions.
    """

    class HasPermissionAccess(BasePermission):
        __permission = permission

        def has_permission(self, request, view):
            space_slug_name = request.headers.get("space", None)
            if space_slug_name is None:
                raise ParseError("space is required")

            policies = Policy.objects.filter(
                spacerole__space__slug_name=space_slug_name,
                spacerole__space_role_user__organization_user_id=request.user.id,
            ).distinct()
            return self.__permission in [
                policy_permission
                for policy in policies
                for policy_permission in policy.permissions
            ]

    return HasPermissionAccess
