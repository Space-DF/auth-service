import logging
from operator import itemgetter

from common.apps.billing.constants import FeatureCode
from common.apps.space.models import Space
from common.celery import constants
from common.celery.tasks import PermanentTaskError, task
from django.db import transaction
from django.db.models import BooleanField, Case, Count, F, IntegerField, Value, When
from django.db.models.functions import Greatest
from django.db.utils import ProgrammingError
from django_tenants.utils import schema_context

logger = logging.getLogger(__name__)


def _is_unlimited(kwargs, feature_code):
    return feature_code in set(kwargs.get("unlimited_features") or [])


@task(
    name="spacedf.tasks.auth_downgrade",
    autoretry_for=(Exception,),
    retry_backoff=2,
    max_retries=3,
)
def auth_downgrade_task(**kwargs):
    org_slug = kwargs["org_slug"]
    limits = kwargs.get("limits") or {}
    max_spaces = limits.get(FeatureCode.SPACE_MAX_COUNT)
    if max_spaces is None:
        raise PermanentTaskError(
            "auth downgrade requires limit %s for org %s"
            % (FeatureCode.SPACE_MAX_COUNT, org_slug)
        )
    if max_spaces < 0:
        raise PermanentTaskError(
            "auth downgrade limit %s must be >= 0 for org %s"
            % (FeatureCode.SPACE_MAX_COUNT, org_slug)
        )

    downgraded_at = kwargs.get("downgraded_at")

    with schema_context(org_slug):
        # 1. fetch all active spaces ordered by owner, then created_at
        # 2. one bulk update of the collected excess ids.
        rows = list(
            Space.objects.filter(is_deactivated=False)
            .values_list("id", "created_by")
            .order_by("created_by", "created_at")
        )
        excess_ids = []
        seen_owner = None
        owner_count = 0
        for space_id, owner_id in rows:
            if owner_id != seen_owner:
                seen_owner = owner_id
                owner_count = 0
            owner_count += 1
            if owner_count > max_spaces:
                excess_ids.append(space_id)

        count = (
            Space.objects.filter(id__in=excess_ids).update(
                is_deactivated=True, deactivated_at=downgraded_at
            )
            if excess_ids
            else 0
        )
        if count:
            logger.info(
                "Downgrade: deactivated %s excess spaces for org %s "
                "(user limit %s).",
                count,
                org_slug,
                max_spaces,
            )
        return count


@task(
    name="spacedf.tasks.auth_upgrade",
    autoretry_for=(Exception,),
    retry_backoff=2,
    max_retries=3,
)
def auth_upgrade_task(**kwargs):
    org_slug = kwargs["org_slug"]
    limits = kwargs.get("limits") or {}
    max_spaces = limits.get(FeatureCode.SPACE_MAX_COUNT)
    unlimited_spaces = _is_unlimited(kwargs, FeatureCode.SPACE_MAX_COUNT)
    if max_spaces is None and not unlimited_spaces:
        raise PermanentTaskError(
            "auth upgrade requires limit or explicit unlimited feature %s for org %s"
            % (FeatureCode.SPACE_MAX_COUNT, org_slug)
        )
    if max_spaces is not None and max_spaces < 0:
        raise PermanentTaskError(
            "auth upgrade limit %s must be >= 0 for org %s"
            % (FeatureCode.SPACE_MAX_COUNT, org_slug)
        )

    with schema_context(org_slug):
        if max_spaces is None:
            count = Space.objects.filter(is_deactivated=True).update(
                is_deactivated=False, deactivated_at=None
            )
        else:
            active_counts = {
                row["created_by"]: row["count"]
                for row in Space.objects.filter(is_deactivated=False)
                .values("created_by")
                .annotate(count=Count("id"))
            }
            reactivated_ids = []
            for space_id, owner_id in (
                Space.objects.filter(is_deactivated=True)
                .values_list("id", "created_by")
                .order_by("created_by", "created_at")
            ):
                owner_active_count = active_counts.get(owner_id, 0)
                if owner_active_count >= max_spaces:
                    continue
                reactivated_ids.append(space_id)
                active_counts[owner_id] = owner_active_count + 1

            count = (
                Space.objects.filter(id__in=reactivated_ids).update(
                    is_deactivated=False, deactivated_at=None
                )
                if reactivated_ids
                else 0
            )
        if count:
            logger.info(
                "Renewal: reactivated %s spaces for org %s.",
                count,
                org_slug,
            )
        return count


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
