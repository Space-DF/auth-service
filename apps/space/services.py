import base64

from common.apps.organization_user.models import OrganizationUser
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

    return (
        queryset.filter(
            space_role__space_role_user__organization_user_id=user_id,
            is_active=True,
        )
        .annotate(
            created_by_display=creator_display,
            total_member_count=Count(
                "space_role__space_role_user__organization_user", distinct=True
            ),
            default_display=Exists(
                SpaceRoleUser.objects.filter(
                    space_role__space=OuterRef("pk"),
                    organization_user_id=user_id,
                    is_default=True,
                )
            ),
        )
        .distinct()
    )
