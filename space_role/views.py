from common.pagination.base_pagination import BasePagination
from common.permissions.constants import DELETE_METHOD, POST_METHOD, UPDATE_METHODS
from common.permissions.permission_classes import is_method
from common.permissions.permission_condition import PermissionCondition
from common.views.space import SpaceListCreateAPIView, SpaceRetrieveUpdateDestroyAPIView
from core.permissions import has_permission_access
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from space_role.constants import Permission
from space_role.models import Policy, SpaceRole
from space_role.serializers import PolicySerializer, SpaceRoleSerializer


class ListCreateSpaceRoleView(SpaceListCreateAPIView):
    model = SpaceRole
    serializer_class = SpaceRoleSerializer
    queryset = SpaceRole.objects.all()
    space_field = "space"
    permission_classes = [
        PermissionCondition.Or(
            PermissionCondition.And(
                is_method(SAFE_METHODS),
                has_permission_access(Permission.READ_ORGANIZATION_ROLE),
            ),
            PermissionCondition.And(
                is_method(POST_METHOD),
                has_permission_access(Permission.CREATE_ORGANIZATION_ROLE),
            ),
        )
    ]
    pagination_class = BasePagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["created_at"]
    search_fields = ["name"]


class UpdateDeleteSpaceRoleView(SpaceRetrieveUpdateDestroyAPIView):
    model = SpaceRole
    serializer_class = SpaceRoleSerializer
    lookup_field = "id"
    queryset = SpaceRole.objects.all()
    space_field = "space"
    permission_classes = [
        PermissionCondition.Or(
            PermissionCondition.And(
                is_method(SAFE_METHODS),
                has_permission_access(Permission.READ_ORGANIZATION_ROLE),
            ),
            PermissionCondition.And(
                is_method(UPDATE_METHODS),
                has_permission_access(Permission.CREATE_ORGANIZATION_ROLE),
            ),
            PermissionCondition.And(
                is_method(DELETE_METHOD),
                has_permission_access(Permission.DELETE_ORGANIZATION_ROLE),
            ),
        )
    ]


class ListPolicyView(ListAPIView):
    model = Policy
    serializer_class = PolicySerializer
    queryset = Policy.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["name"]
    search_fields = ["name"]


class RetrievePolicyView(RetrieveAPIView):
    model = Policy
    serializer_class = PolicySerializer
    lookup_field = "id"
    queryset = Policy.objects.all()
    permission_classes = [IsAuthenticated]
