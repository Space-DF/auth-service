import secrets
import string
from operator import itemgetter
from typing import Literal

import requests
from common.apps.organization_user.models import OrganizationUser
from common.apps.refresh_tokens.services import create_jwt_tokens
from common.apps.space_role.models import SpacePolicy, SpaceRoleUser
from django.conf import settings
from django.core.cache import cache
from django.db.models import Prefetch
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


def create_space_access_token(user_id, access_token):
    space_permissions_cache = cache.get(f"space_permissions_{user_id}")
    if space_permissions_cache:
        access_token["space_permissions"] = space_permissions_cache
        return access_token
    role_users = (
        SpaceRoleUser.objects.filter(organization_user_id=user_id)
        .select_related("space_role__space")
        .prefetch_related(
            Prefetch(
                "space_role__policies",
                queryset=SpacePolicy.objects.all(),
                to_attr="space_policies",
            )
        )
        .order_by("space_role__space_id")
        .distinct("space_role__space_id")
    )
    space_permissions = {}
    for role_user in role_users:
        space_slug = str(role_user.space_role.space.slug_name)
        if space_slug not in space_permissions:
            space_permissions[space_slug] = set()
        for policy in getattr(role_user.space_role, "space_policies", []):
            space_permissions[space_slug].update(policy.permissions)
    space_permissions_dict = {
        space_slug: list(permissions)
        for space_slug, permissions in space_permissions.items()
    }
    cache.set(
        f"space_permissions_{user_id}",
        space_permissions_dict,
        timeout=60 * 60 * 24,
    )
    access_token["space_permissions"] = space_permissions_dict
    return access_token


def create_space_jwt_tokens(user, space_slug, issuer=None, **kwargs):
    refresh_token, access_token = create_jwt_tokens(user, issuer, **kwargs)
    if space_slug:
        access_token = create_space_access_token(user.id, access_token)
    return refresh_token, access_token


def handle_space_access_token(request, access_token, provider: Literal["GOOGLE"]):
    info_url = settings.OAUTH_CLIENTS[provider]["INFO_URL"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(url=info_url, headers=headers, timeout=10)
    response.raise_for_status()
    user_info_dict = response.json()
    given_name, family_name, email = itemgetter("given_name", "family_name", "email")(
        user_info_dict
    )
    organization_user, is_created = OrganizationUser.objects.get_or_create(
        email=email,
    )
    if is_created:
        organization_user.first_name = given_name
        organization_user.last_name = family_name
        organization_user.save()

    if provider.lower() not in organization_user.providers:
        organization_user.providers.append(provider.lower())
        organization_user.save()

    default_space_slug = f"default-{organization_user.id}"

    refresh, access = create_space_jwt_tokens(
        organization_user, space_slug=default_space_slug, issuer=request.tenant
    )
    return Response(
        status=status.HTTP_200_OK, data={"refresh": str(refresh), "access": str(access)}
    )


def generate_otp(length=6):
    """Generate a 6-digit OTP."""
    return "".join(secrets.choice(string.digits) for _ in range(length))


def render_email_format(template, data):
    try:
        html_message = render_to_string(
            template,
            data,
        )
        return html_message
    except Exception as e:
        raise ValidationError({"error": f"Error: {e}"})
