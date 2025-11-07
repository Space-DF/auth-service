from common.apps.space.models import Space
from common.apps.space_role.models import SpacePolicy, SpaceRole, SpaceRoleUser
from common.pagination.base_pagination import BasePagination
from common.views.space import (
    SpaceListAPIView,
    SpaceListCreateAPIView,
    SpaceRetrieveUpdateDestroyAPIView,
)
from django.db.models import BooleanField, Case, When
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
from utils.permissions_classes import IsSpaceAdmin


class ListCreateSpaceRoleView(SpaceListCreateAPIView):
    model = SpaceRole
    serializer_class = SpaceRoleSerializer
    queryset = SpaceRole.objects.all()
    space_field = "space"
    pagination_class = BasePagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["created_at"]
    search_fields = ["name"]

    def get_permissions(self):
        if self.request.method in ["POST"]:
            return [IsSpaceAdmin()]
        return super().get_permissions()


class UpdateDeleteSpaceRoleView(SpaceRetrieveUpdateDestroyAPIView):
    model = SpaceRole
    serializer_class = SpaceRoleSerializer
    lookup_field = "id"
    queryset = SpaceRole.objects.all()
    space_field = "space"

    def get_permissions(self):
        if self.request.method in ["DELETE", "PUT", "PATCH"]:
            return [IsSpaceAdmin()]
        return super().get_permissions()


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

    def get_permissions(self):
        if self.request.method in ["DELETE", "PUT", "PATCH"]:
            return [IsSpaceAdmin()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return SpaceRoleUserUpdateSerializer
        return super().get_serializer_class()


class SpaceRoleUserDefaultView(APIView):
    permission_classes = [IsSpaceAdmin]

    def post(self, request, *args, **kwargs):
        instance = get_object_or_404(Space, id=kwargs.get("id"))
        user_id = request.headers.get("X-User-ID", None)
        if not user_id:
            return Response(
                {"error": "X-User-ID header missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        SpaceRoleUser.objects.filter(organization_user_id=user_id).update(
            is_default=Case(
                When(space_role__space_id=instance.id, then=True),
                default=False,
                output_field=BooleanField(),
            )
        )
        return Response(
            {"result": "Set default for Space successful"}, status=status.HTTP_200_OK
        )
