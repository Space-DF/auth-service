from common.apps.organization_user.models import OrganizationUser
from common.apps.space.models import Space
from common.apps.space_role.models import SpaceRole, SpaceRoleUser
from common.pagination.base_pagination import BasePagination
from common.utils.send_email import send_email
from common.views.space import SpaceListCreateAPIView, SpaceRetrieveUpdateDestroyAPIView
from django.core.cache import cache
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from django.conf import settings

from apps.space.serializers import InviteUserSerial, SpaceSerializer
from apps.space.service import decode_token, generate_token, render_email_format


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


class InviteUserAPIView(generics.CreateAPIView):
    serializer_class = InviteUserSerial

    def get_object(self):
        user_id = self.request.headers.get("X-User-ID", None)
        if not user_id:
            raise NotFound("The user not found!")
        return get_object_or_404(OrganizationUser, id=user_id)

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        list_email = serializer.data.get("receiver_list")
        space_id = kwargs.get("space_id")
        space = get_object_or_404(Space, id=space_id)
        subject = "The invitation"
        name_sender = instance.first_name + " " + instance.last_name

        for email_receiver in list_email:
            token = generate_token(
                email_receiver, request.tenant.slug_name, space_id
            )
            invite_url = request.build_absolute_uri(
                reverse("space:join_space", kwargs={"token": token})
            )
            message = render_email_format(
                name_sender, email_receiver, space.name, invite_url
            )
            cache.set(f"invite_{email_receiver}_{space_id}", token, timeout=604800)
            send_email(settings.DEFAULT_FROM_EMAIL, list_email, subject, message)
        return Response(
            {"result": "Invitation sent successfully"},
            status=status.HTTP_200_OK,
        )


class AddUserToSpaceAPIView(generics.RetrieveAPIView):

    def get(self, request, *args, **kwargs):
        token = kwargs.get("token")
        space_id, email_receiver, slug_name = decode_token(token)
        key_token = f"invite_{email_receiver}_{space_id}"
        if key_token not in cache.keys("invite_*"):
            return redirect(f"https://{slug_name}.spacedf.net/invitation?status=failed")

        user_organization = OrganizationUser.objects.filter(
            email=email_receiver
        ).first()
        if not user_organization:
            return redirect(f"https://{slug_name}.spacedf.net?token={token}")

        try:
            with transaction.atomic():
                space_role = SpaceRole.objects.filter(
                    space_id=space_id, name="Reader"
                ).first()
                SpaceRoleUser.objects.get_or_create(
                    space_role=space_role, organization_user=user_organization
                )
                return redirect(
                    f"https://{slug_name}.spacedf.net/invitation?status=success"
                )
        except Exception:
            return redirect(f"https://{slug_name}.spacedf.net/invitation?status=failed")
