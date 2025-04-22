from common.apps.space.models import Space
from common.apps.space_role.models import SpacePolicy, SpaceRole, SpaceRoleUser
from common.pagination.base_pagination import BasePagination
from common.views.space import (
    SpaceListAPIView,
    SpaceListCreateAPIView,
    SpaceRetrieveUpdateDestroyAPIView,
)
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.space_role.serializers import (
    SpacePolicySerializer,
    SpaceRoleSerializer,
    SpaceRoleUserSerializer,
    SpaceRoleUserUpdateSerializer,
)
from apps.space_role.services import create_space_default_role


class ListCreateSpaceRoleView(SpaceListCreateAPIView):
    model = SpaceRole
    serializer_class = SpaceRoleSerializer
    queryset = SpaceRole.objects.all()
    space_field = "space"
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


class ListSpacePolicyView(ListAPIView):
    model = SpacePolicy
    serializer_class = SpacePolicySerializer
    queryset = SpacePolicy.objects.all()
    pagination_class = BasePagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["name"]
    search_fields = ["name"]


class RetrieveSpacePolicyView(RetrieveAPIView):
    model = SpacePolicy
    serializer_class = SpacePolicySerializer
    lookup_field = "id"
    queryset = SpacePolicy.objects.all()


class ListSpaceRoleUserView(SpaceListAPIView):
    model = SpaceRoleUser
    serializer_class = SpaceRoleUserSerializer
    queryset = SpaceRoleUser.objects.select_related("space_role", "organization_user")
    space_field = "space_role__space"
    pagination_class = BasePagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["created_at"]
    search_fields = [
        "organization_user__first_name",
        "organization_user__last_name",
        "organization_user__email",
    ]


class RetrieveDeleteSpaceRoleUserView(SpaceRetrieveUpdateDestroyAPIView):
    model = SpaceRoleUser
    serializer_class = SpaceRoleUserSerializer
    lookup_field = "id"
    queryset = SpaceRoleUser.objects.select_related("space_role", "organization_user")
    space_field = "space_role__space"

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return SpaceRoleUserUpdateSerializer
        return super().get_serializer_class()


@receiver(post_save, sender=Space)
@transaction.atomic
def handle_new_space(sender, instance, created, **kwargs):
    if created:
        owner_role, _ = create_space_default_role(instance)
        has_any_space = SpaceRoleUser.objects.filter(
            organization_user_id=instance.created_by
        ).exists()

        SpaceRoleUser.objects.create(
            organization_user_id=instance.created_by,
            space_role=owner_role,
            is_default=not has_any_space,
        )


class SpaceRoleUserDefaultView(APIView):

    def post(self, request, *args, **kwargs):
        instance = get_object_or_404(Space, id=kwargs.get("id"))
        user_id = request.headers.get("X-User-ID", None)
        if not user_id:
            return Response(
                {"error": "X-User-ID header missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        SpaceRoleUser.objects.filter(
            organization_user_id=user_id, is_default=True
        ).update(is_default=False)
        SpaceRoleUser.objects.filter(
            organization_user_id=user_id, space_role__space_id=instance.id
        ).update(is_default=True)
        return Response(
            {"result": "Set default for Space successful"}, status=status.HTTP_200_OK
        )
