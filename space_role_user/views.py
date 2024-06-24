from common.pagination.base_pagination import BasePagination
from common.permissions.constants import DELETE_METHOD
from common.permissions.permission_classes import is_method
from common.permissions.permission_condition import PermissionCondition
from common.views.space import SpaceListAPIView, SpaceRetrieveDestroyAPIView
from core.permissions import has_permission_access
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import SAFE_METHODS
from space_role.constants import Permission
from space_role_user.models import SpaceRoleUser
from space_role_user.serializers import SpaceRoleUserSerializer


class ListSpaceRoleUserView(SpaceListAPIView):
    model = SpaceRoleUser
    serializer_class = SpaceRoleUserSerializer
    queryset = SpaceRoleUser.objects.all()
    space_field = "space_role__space"
    permission_classes = [has_permission_access(Permission.READ_ORGANIZATION_MEMBER)]
    pagination_class = BasePagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["created_at"]
    search_fields = ["id"]


class RetrieveDeleteSpaceRoleUserView(SpaceRetrieveDestroyAPIView):
    model = SpaceRoleUser
    serializer_class = SpaceRoleUserSerializer
    lookup_field = "id"
    queryset = SpaceRoleUser.objects.all()
    space_field = "space_role__space"
    permission_classes = [
        PermissionCondition.Or(
            PermissionCondition.And(
                is_method(SAFE_METHODS),
                has_permission_access(Permission.READ_ORGANIZATION_MEMBER),
            ),
            PermissionCondition.And(
                is_method(DELETE_METHOD),
                has_permission_access(Permission.REMOVE_ORGANIZATION_MEMBER),
            ),
        )
    ]
