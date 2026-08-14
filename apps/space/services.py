import base64

from common.apps.organization_user.models import OrganizationUser
from common.apps.space.models import Space
from common.apps.space_role.models import SpaceRoleUser
from django.db.models import (
    Case,
    CharField,
    Count,
    Exists,
    F,
    OuterRef,
    Subquery,
    Value,
    When,
)
from django.db.models.functions import Coalesce, Concat, Length, Trim


def encode_image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def get_spaces_queryset_for_user(queryset, user_id):
    creator_display = Subquery(
        OrganizationUser.objects.filter(id=OuterRef("created_by"))
        .annotate(
            full_name=Concat(
                Coalesce(F("first_name"), Value("")),
                Value(" "),
                Coalesce(F("last_name"), Value("")),
                output_field=CharField(),
            )
        )
        .annotate(full_len=Length(Trim(F("full_name"))))
        .annotate(
            value=Case(
                When(full_len__gt=0, then=F("full_name")),
                default=Concat(Value(""), F("email"), output_field=CharField()),
                output_field=CharField(),
            )
        )
        .values("value")[:1]
    )

    user_membership = SpaceRoleUser.objects.filter(
        space_role__space=OuterRef("pk"),
        organization_user_id=user_id,
    )

    default_membership = user_membership.filter(is_default=True)

    total_member_count = Subquery(
        SpaceRoleUser.objects.filter(space_role__space=OuterRef("pk"))
        .values("space_role__space")
        .annotate(count=Count("organization_user_id", distinct=True))
        .values("count")[:1]
    )

    return (
        queryset.filter(is_active=True)
        .filter(Exists(user_membership))
        .annotate(
            created_by_display=creator_display,
            total_member_count=Coalesce(total_member_count, Value(0)),
            default_display=Exists(default_membership),
        )
    )


def get_users_default_spaces_payload(user_ids):
    user_ids = list(user_ids)
    default_spaces = {
        str(item["created_by"]): item["slug_name"]
        for item in Space.objects.filter(
            created_by__in=user_ids,
            is_default=True,
            is_active=True,
        ).values("created_by", "slug_name")
    }

    users = [
        {
            "id": str(user_id),
            "slug_name": default_spaces.get(str(user_id)),
        }
        for user_id in user_ids
    ]
    return {
        "total_users": len(user_ids),
        "users": users,
    }
