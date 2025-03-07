from common.apps.organization_user.models import OrganizationUser
from common.apps.space.models import Space
from common.apps.space_role.constants import SpacePermission
from common.pagination.base_pagination import BasePagination
from common.swagger.params import get_space_header_params
from common.views.space import SpaceListCreateAPIView, SpaceRetrieveUpdateDestroyAPIView
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404

from apps.space.serializers import SpaceSerializer


class SpaceView(SpaceListCreateAPIView, SpaceRetrieveUpdateDestroyAPIView):
    model = Space
    serializer_class = SpaceSerializer
    queryset = Space.objects.all()
    pagination_class = BasePagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["created_at"]
    search_fields = ["name"]

    def get_queryset(self):
        queryset = self.queryset.filter(
            space_role__space_role_user__organization_user_id=self.request.user.id,
            is_active=True,
        ).distinct()

        return queryset

    def get_object(self):
        obj = get_object_or_404(
            self.get_queryset(),
            slug_name=self.request.headers.get("X-Space", None),
        )

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @swagger_auto_schema(manual_parameters=get_space_header_params(required=False))
    def get(self, request, *args, **kwargs):
        if self.request.headers.get("X-Space", None) is not None:
            return self.retrieve(request, *args, **kwargs)
        else:
            return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


@receiver(post_save, sender=OrganizationUser)
def create_default_space(sender, instance, created, **kwargs):
    if created:
        Space(
            name="Default",
            slug_name=f"default-{instance.id}",
            created_by=instance,
        ).save()
