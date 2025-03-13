from common.apps.organization_user.models import OrganizationUser
from common.apps.space.models import Space
from common.pagination.base_pagination import BasePagination
from common.views.space import SpaceListCreateAPIView, SpaceRetrieveUpdateDestroyAPIView
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
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

    def get_object(self):
        space_slug = self.request.headers.get("X-Space", None)
        if not space_slug:
            return None
        return get_object_or_404(Space, slug_name=space_slug)

    def get_queryset(self):
        user_id = self.request.headers.get("X-User-ID", None)
        if not user_id:
            return self.queryset.none()
        queryset = self.queryset.filter(
            space_role__space_role_user__organization_user_id=user_id,
            is_active=True,
        ).distinct()

        return queryset

    @transaction.atomic
    def perform_create(self, serializer):
        user_id = self.request.headers.get("X-User-ID", "")
        organization_user = get_object_or_404(OrganizationUser, id=user_id)
        serializer.save(created_by=organization_user.id)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


@receiver(post_save, sender=OrganizationUser)
def create_default_space(sender, instance, created, **kwargs):
    if created:
        Space(
            name="Default",
            slug_name=f"default-{instance.id}",
            created_by=instance.id,
        ).save()
