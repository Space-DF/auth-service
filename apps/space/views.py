from common.apps.organization_user.models import OrganizationUser
from common.apps.space.models import Space
from common.apps.space_role.models import SpaceRole, SpaceRoleUser
from common.pagination.base_pagination import BasePagination
from common.utils.send_email import send_email
from common.utils.token_jwt import generate_token
from common.views.space import SpaceListCreateAPIView, SpaceRetrieveUpdateDestroyAPIView
from django.conf import settings
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, UntypedToken

from apps.space.serializers import InviteUserSerial, SpaceSerializer
from apps.space.service import render_email_format


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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_default:
            return Response(
                {"detail": "Cannot delete default Space"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_ids = OrganizationUser.objects.filter(
            space_role_user__space_role__space_id=instance.id,
            space_role_user__is_default=True,
        ).values_list("id", flat=True)

        space_ids = Space.objects.filter(
            created_by__in=user_ids, is_default=True
        ).values_list("id", flat=True)

        SpaceRoleUser.objects.filter(
            organization_user_id__in=user_ids, space_role__space_id__in=space_ids
        ).update(is_default=True)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


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
                {
                    "email_receiver": receiver_email,
                    "org_slug_name": request.tenant.slug_name,
                    "space_role_id": receiver_item.get("space_role_id"),
                },
                10080,
            )
            invite_url = request.build_absolute_uri(
                reverse("space:join_space_redirect", kwargs={"token": token})
            )
            message = render_email_format(
                name_sender, receiver_email, space.name, invite_url
            )
            send_email(settings.DEFAULT_FROM_EMAIL, [receiver_email], subject, message)
        return Response(
            {"result": "Invitation sent successfully"},
            status=status.HTTP_200_OK,
        )


class RedirectAddUserToSpaceAPIView(APIView):
    def get(self, request, *args, **kwargs):
        token_str = kwargs.get("token")
        org_slug_name = ""
        try:
            org_slug_name = UntypedToken(token_str, verify=False).payload.get(
                "org_slug_name"
            )
            token = AccessToken(token_str)
        except Exception:
            return redirect(
                f"https://{org_slug_name}.spacedf.net/invitation?status=failed"
            )

        email_receiver = token.get("email_receiver")
        space_role_id = token.get("space_role_id")

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
        token_str = kwargs.get("token")
        try:
            token = AccessToken(token_str)
        except Exception:
            return Response({"error": "Invalid or expired invitation"}, status=400)

        email_receiver = token.get("email_receiver")
        space_role_id = token.get("space_role_id")

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
