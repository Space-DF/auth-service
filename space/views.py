from common.pagination.base_pagination import BasePagination
from common.permissions.constants import DELETE_METHOD, POST_METHOD, UPDATE_METHODS
from common.permissions.permission_classes import is_method
from common.permissions.permission_condition import PermissionCondition
from common.swagger.params import get_space_header_params
from common.views.space import SpaceListCreateAPIView, SpaceRetrieveUpdateDestroyAPIView
from core.permissions import has_permission_access
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from space.models import Space
from space.serializers import SpaceSerializer
from space_role.constants import Permission
from space_role.models import Policy, SpaceRole
from space_role_user.models import SpaceRoleUser


class SpaceView(SpaceListCreateAPIView, SpaceRetrieveUpdateDestroyAPIView):
    model = Space
    serializer_class = SpaceSerializer
    queryset = Space.objects.all()
    permission_classes = [
        PermissionCondition.Or(
            PermissionCondition.And(is_method(SAFE_METHODS), IsAuthenticated),
            PermissionCondition.And(is_method(POST_METHOD), IsAuthenticated),
            PermissionCondition.And(
                is_method(UPDATE_METHODS),
                has_permission_access(Permission.UPDATE_ORGANIZATION),
            ),
            PermissionCondition.And(
                is_method(DELETE_METHOD),
                has_permission_access(Permission.DELETE_ORGANIZATION),
            ),
        )
    ]
    pagination_class = BasePagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["created_at"]
    search_fields = ["name"]

    def get_queryset(self):
        queryset = self.queryset.filter(
            space_role__space_role_user__organization_user_id=self.request.user.id,
            is_active=True,
        ).distinct()

        if (
            self.request.method not in SAFE_METHODS
            or self.request.headers.get("space", None) is not None
        ):
            queryset = queryset.filter(
                slug_name=self.request.headers.get("space", None)
            )

        return queryset

    def get_object(self):
        obj = get_object_or_404(
            self.get_queryset(),
            slug_name=self.request.headers.get("space", None),
        )

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def create_default_role_by_policy_tag(self, space, name, tag):
        policies = Policy.objects.filter(tags__icontains=tag).all()
        space_role = SpaceRole(name=name, space=space)
        space_role.save()

        SpaceRolePolicy = SpaceRole.policies.through
        SpaceRolePolicy.objects.bulk_create(
            [
                SpaceRolePolicy(spacerole_id=space_role.pk, policy_id=policy.pk)
                for policy in policies
            ]
        )

        return space_role

    @transaction.atomic
    def perform_create(self, serializer):
        space = serializer.save()

        owner_role = self.create_default_role_by_policy_tag(
            space, "Owner", "administrator"
        )
        self.create_default_role_by_policy_tag(space, "Reader", "read-only")

        SpaceRoleUser(organization_user=self.request.user, space_role=owner_role).save()

    @swagger_auto_schema(manual_parameters=get_space_header_params(required=False))
    def get(self, request, *args, **kwargs):
        if self.request.headers.get("space", None) is not None:
            return self.retrieve(request, *args, **kwargs)
        else:
            return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
