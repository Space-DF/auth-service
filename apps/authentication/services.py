import secrets
import string
from operator import itemgetter
from typing import Literal

import requests
from common.apps.organization_user.models import OrganizationUser
from common.apps.refresh_tokens.services import create_jwt_tokens
from django.conf import settings
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


def create_space_jwt_tokens(user, slug_name, issuer=None, **kwargs):
    refresh_token, access_token = create_jwt_tokens(user, issuer, **kwargs)
    if slug_name:
        access_token["space"] = slug_name
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
        organization_user.set_unusable_password()
        organization_user.save()
    elif not organization_user.password:
        organization_user.set_unusable_password()
        organization_user.save(update_fields=["password"])

    if provider.lower() not in organization_user.providers:
        organization_user.providers.append(provider.lower())
        organization_user.save()

    default_space_slug = f"default-{organization_user.id}"

    refresh, access = create_space_jwt_tokens(
        organization_user, space_slug=default_space_slug, issuer=request.tenant
    )
    return Response(
        status=status.HTTP_200_OK,
        data={
            "refresh": str(refresh),
            "access": str(access),
            "default_space": default_space_slug,
        },
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
