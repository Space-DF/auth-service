from common.apps.space.models import Space
from common.apps.space_role.constants import SpacePermission
from common.apps.space_role.models import SpacePolicy, SpaceRole, SpaceRoleUser
from common.pagination.base_pagination import BasePagination
from common.permissions.constants import DELETE_METHOD, POST_METHOD, UPDATE_METHODS
from common.permissions.permission_classes import has_space_permission_access, is_method
from common.permissions.permission_condition import PermissionCondition
from common.views.space import (
    SpaceListAPIView,
    SpaceListCreateAPIView,
    SpaceRetrieveDestroyAPIView,
    SpaceRetrieveUpdateDestroyAPIView,
)
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated

from apps.space_role.serializers import (
    SpacePolicySerializer,
    SpaceRoleSerializer,
    SpaceRoleUserSerializer,
)
from apps.space_role.services import create_space_default_role


class ListCreateSpaceRoleView(SpaceListCreateAPIView):
    model = SpaceRole
    serializer_class = SpaceRoleSerializer
    queryset = SpaceRole.objects.all()
    space_field = "space"
    permission_classes = [
        IsAuthenticated,
        PermissionCondition.Or(
            PermissionCondition.And(
                is_method(SAFE_METHODS),
                has_space_permission_access(SpacePermission.READ_SPACE_ROLE),
            ),
            PermissionCondition.And(
                is_method(POST_METHOD),
                has_space_permission_access(SpacePermission.CREATE_SPACE_ROLE),
            ),
        ),
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
        IsAuthenticated,
        PermissionCondition.Or(
            PermissionCondition.And(
                is_method(SAFE_METHODS),
                has_space_permission_access(SpacePermission.READ_SPACE_ROLE),
            ),
            PermissionCondition.And(
                is_method(UPDATE_METHODS),
                has_space_permission_access(SpacePermission.CREATE_SPACE_ROLE),
            ),
            PermissionCondition.And(
                is_method(DELETE_METHOD),
                has_space_permission_access(SpacePermission.DELETE_SPACE_ROLE),
            ),
        ),
    ]


class ListSpacePolicyView(ListAPIView):
    model = SpacePolicy
    serializer_class = SpacePolicySerializer
    queryset = SpacePolicy.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["name"]
    search_fields = ["name"]


class RetrieveSpacePolicyView(RetrieveAPIView):
    model = SpacePolicy
    serializer_class = SpacePolicySerializer
    lookup_field = "id"
    queryset = SpacePolicy.objects.all()
    permission_classes = [IsAuthenticated]


class ListSpaceRoleUserView(SpaceListAPIView):
    model = SpaceRoleUser
    serializer_class = SpaceRoleUserSerializer
    queryset = SpaceRoleUser.objects.all()
    space_field = "space_role__space"
    permission_classes = [
        has_space_permission_access(SpacePermission.READ_SPACE_MEMBER)
    ]
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
        IsAuthenticated,
        PermissionCondition.Or(
            PermissionCondition.And(
                is_method(SAFE_METHODS),
                has_space_permission_access(SpacePermission.READ_SPACE_MEMBER),
            ),
            PermissionCondition.And(
                is_method(DELETE_METHOD),
                has_space_permission_access(SpacePermission.REMOVE_SPACE_MEMBER),
            ),
        ),
    ]


@receiver(post_save, sender=Space)
@transaction.atomic
def handle_new_space(sender, instance, created, **kwargs):
    if created:
        owner_role, _ = create_space_default_role(instance)
        SpaceRoleUser(
            organization_user=instance.created_by, space_role=owner_role
        ).save()
