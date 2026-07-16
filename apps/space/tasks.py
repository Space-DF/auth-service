import logging
from operator import itemgetter

from common.apps.space.models import Space
from common.celery import constants
from common.celery.tasks import task
from django.db import transaction
from django.db.models import BooleanField, Case, F, IntegerField, Value, When
from django.db.models.functions import Greatest
from django.db.utils import ProgrammingError
from django_tenants.utils import schema_context

logger = logging.getLogger(__name__)


@task(
    name="spacedf.tasks.space_downgrade",
    autoretry_for=(Exception,),
    retry_backoff=2,
    max_retries=3,
)
def space_downgrade_task(**kwargs):
    return deactivate_excess_spaces(kwargs["org_slug"], kwargs.get("limits"))


@task(
    name="spacedf.tasks.space_upgrade",
    autoretry_for=(Exception,),
    retry_backoff=2,
    max_retries=3,
)
def space_upgrade_task(**kwargs):
    return reactivate_spaces(kwargs["org_slug"])


# TODO: need function on device service call this task
@task(
    name=f"spacedf.tasks.{constants.AUTH_SERVICE_ADD_OR_REMOVE_DEVICE}",
    autoretry_for=(ProgrammingError,),
    retry_backoff=2,
    max_retries=3,
)
@transaction.atomic
def add_or_remove_device(**kwargs):
    slug_name, space_slug_name, action_type = itemgetter(
        "slug_name", "space_slug_name", "type"
    )(kwargs)
    with schema_context(slug_name):
        value = Case(
            When(
                Value(action_type == "add", output_field=BooleanField()), then=Value(1)
            ),
            When(
                Value(action_type == "remove", output_field=BooleanField()),
                then=Value(-1),
            ),
            default=Value(0),
            output_field=IntegerField(),
        )

        Space.objects.filter(slug_name=space_slug_name).update(
            total_devices=Greatest(F("total_devices") + value, Value(0)),
        )


def deactivate_excess_spaces(organization_slug: str, limits: dict = None) -> int:
    limits = limits or {}
    max_spaces = limits.get("space.max_count")
    if max_spaces is None:
        logger.warning(
            "Skipping space deactivation for %s: space.max_count not in event",
            organization_slug,
        )
        return 0

    with schema_context(organization_slug):
        spaces = Space.objects.filter(is_deactivated=False).order_by("created_at")
        total = spaces.count()
        excess_ids = list(spaces.values_list("id", flat=True)[max_spaces:])
        count = (
            Space.objects.filter(id__in=excess_ids).update(is_deactivated=True)
            if excess_ids
            else 0
        )
        if count:
            logger.info(
                "Downgrade: deactivated %s excess spaces for org %s "
                "(kept %s active out of %s total).",
                count,
                organization_slug,
                min(total, max_spaces),
                total,
            )
        return count


def reactivate_spaces(organization_slug: str) -> int:
    """
    Reactivate spaces that were deactivated during a prior downgrade.
    """
    with schema_context(organization_slug):
        count = Space.objects.filter(is_deactivated=True).update(is_deactivated=False)
        if count:
            logger.info(
                "Renewal: reactivated %s spaces for org %s.",
                count,
                organization_slug,
            )
        return count
