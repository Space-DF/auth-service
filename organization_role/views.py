from common.apps.organization_role.constants import OrganizationPermission
from common.apps.organization_role.models import (
    OrganizationPolicy,
    OrganizationRole,
    OrganizationRoleUser,
)
from common.pagination.base_pagination import BasePagination
from common.permissions.constants import DELETE_METHOD, POST_METHOD, UPDATE_METHODS
from common.permissions.permission_classes import (
    has_organization_permission_access,
    is_method,
)
from common.permissions.permission_condition import PermissionCondition
from organization_role.serializers import (
    OrganizationPolicySerializer,
    OrganizationRoleSerializer,
    OrganizationRoleUserSerializer,
)
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveDestroyAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated


class ListCreateOrganizationRoleView(ListCreateAPIView):
    model = OrganizationRole
    serializer_class = OrganizationRoleSerializer
    queryset = OrganizationRole.objects.all()
    organization_field = "organization"
    permission_classes = [
        PermissionCondition.Or(
            PermissionCondition.And(
                is_method(SAFE_METHODS),
                has_organization_permission_access(
                    OrganizationPermission.READ_ORGANIZATION_ROLE
                ),
            ),
            PermissionCondition.And(
                is_method(POST_METHOD),
                has_organization_permission_access(
                    OrganizationPermission.CREATE_ORGANIZATION_ROLE
                ),
            ),
        )
    ]
    pagination_class = BasePagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["created_at"]
    search_fields = ["name"]


class UpdateDeleteOrganizationRoleView(RetrieveUpdateDestroyAPIView):
    model = OrganizationRole
    serializer_class = OrganizationRoleSerializer
    lookup_field = "id"
    queryset = OrganizationRole.objects.all()
    organization_field = "organization"
    permission_classes = [
        PermissionCondition.Or(
            PermissionCondition.And(
                is_method(SAFE_METHODS),
                has_organization_permission_access(
                    OrganizationPermission.READ_ORGANIZATION_ROLE
                ),
            ),
            PermissionCondition.And(
                is_method(UPDATE_METHODS),
                has_organization_permission_access(
                    OrganizationPermission.CREATE_ORGANIZATION_ROLE
                ),
            ),
            PermissionCondition.And(
                is_method(DELETE_METHOD),
                has_organization_permission_access(
                    OrganizationPermission.DELETE_ORGANIZATION_ROLE
                ),
            ),
        )
    ]


class ListOrganizationPolicyView(ListAPIView):
    model = OrganizationPolicy
    serializer_class = OrganizationPolicySerializer
    queryset = OrganizationPolicy.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["name"]
    search_fields = ["name"]


class RetrieveOrganizationPolicyView(RetrieveAPIView):
    model = OrganizationPolicy
    serializer_class = OrganizationPolicySerializer
    lookup_field = "id"
    queryset = OrganizationPolicy.objects.all()
    permission_classes = [IsAuthenticated]


class ListOrganizationRoleUserView(ListAPIView):
    model = OrganizationRoleUser
    serializer_class = OrganizationRoleUserSerializer
    queryset = OrganizationRoleUser.objects.all()
    organization_field = "organization_role__organization"
    permission_classes = [
        has_organization_permission_access(
            OrganizationPermission.READ_ORGANIZATION_MEMBER
        )
    ]
    pagination_class = BasePagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["created_at"]
    search_fields = ["id"]


class RetrieveDeleteOrganizationRoleUserView(RetrieveDestroyAPIView):
    model = OrganizationRoleUser
    serializer_class = OrganizationRoleUserSerializer
    lookup_field = "id"
    queryset = OrganizationRoleUser.objects.all()
    organization_field = "organization_role__organization"
    permission_classes = [
        PermissionCondition.Or(
            PermissionCondition.And(
                is_method(SAFE_METHODS),
                has_organization_permission_access(
                    OrganizationPermission.READ_ORGANIZATION_MEMBER
                ),
            ),
            PermissionCondition.And(
                is_method(DELETE_METHOD),
                has_organization_permission_access(
                    OrganizationPermission.REMOVE_ORGANIZATION_MEMBER
                ),
            ),
        )
    ]
