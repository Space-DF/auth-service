"""Space downgrade deactivation logic."""

import logging

from common.apps.space.models import Space
from django_tenants.utils import schema_context

logger = logging.getLogger(__name__)


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
