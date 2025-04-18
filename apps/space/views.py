from common.apps.organization_user.models import OrganizationUser
from common.apps.space.models import Space
from common.apps.space_role.models import SpaceRole, SpaceRoleUser
from common.pagination.base_pagination import BasePagination
from common.utils.send_email import send_email
from common.views.space import SpaceListCreateAPIView, SpaceRetrieveUpdateDestroyAPIView
from django.conf import settings
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
from rest_framework.views import APIView
from rest_framework.exceptions import ParseError

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
        receiver_list = serializer.data.get("receiver_list")
        space_slug_name = self.request.headers.get("X-Space", None)
        if space_slug_name is None:
            raise ParseError("X-Space header is required")
        space = get_object_or_404(Space, slug_name=space_slug_name)
        subject = "The invitation"
        name_sender = instance.first_name + " " + instance.last_name

        for receiver_item in receiver_list:
            receiver_email = receiver_item.get("email")
            token = generate_token(
                receiver_email,
                request.tenant.slug_name,
                space_slug_name,
                receiver_item.get("space_role_id"),
            )
            invite_url = request.build_absolute_uri(
                reverse("space:join_space_redirect", kwargs={"token": token})
            )
            message = render_email_format(
                name_sender, receiver_email, space.name, invite_url
            )
            cache.set(
                f"invite_{receiver_email}_{request.tenant.slug_name}_{space_slug_name}",
                token,
                timeout=604800,
            )
            send_email(settings.DEFAULT_FROM_EMAIL, [receiver_email], subject, message)
        return Response(
            {"result": "Invitation sent successfully"},
            status=status.HTTP_200_OK,
        )


class RedirectAddUserToSpaceAPIView(APIView):

    def get(self, request, *args, **kwargs):
        token = kwargs.get("token")
        space_slug_name, email_receiver, org_slug_name, space_role_id = decode_token(
            token
        )
        key_token = f"invite_{email_receiver}_{org_slug_name}_{space_slug_name}"
        if not cache.get(key_token):
            return redirect(
                f"https://{org_slug_name}.spacedf.net/invitation?status=failed"
            )

        user_organization = OrganizationUser.objects.filter(
            email=email_receiver
        ).first()
        if not user_organization:
            return redirect(f"https://{org_slug_name}.spacedf.net?token={token}")

        space_role = SpaceRole.objects.get(id=space_role_id)
        SpaceRoleUser.objects.get_or_create(
            space_role=space_role, organization_user=user_organization
        )
        return redirect(
            f"https://{org_slug_name}.spacedf.net/invitation?status=success"
        )


class AddUserToSpaceAPIView(APIView):

    def get(self, request, *args, **kwargs):
        token = kwargs.get("token")
        space_slug_name, email_receiver, org_slug_name, space_role_id = decode_token(
            token
        )
        key_token = f"invite_{email_receiver}_{org_slug_name}_{space_slug_name}"
        if not cache.get(key_token):
            return Response({"error": "Invalid or expired invitation"}, status=400)

        user_organization = OrganizationUser.objects.filter(
            email=email_receiver
        ).first()
        if not user_organization:
            return Response({"error": "User not found in organization"}, status=400)

        space_role = SpaceRole.objects.get(id=space_role_id)
        SpaceRoleUser.objects.get_or_create(
            space_role=space_role, organization_user=user_organization
        )
        return Response({"result": "User added successfully"}, status=200)
