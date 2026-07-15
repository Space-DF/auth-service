"""Space downgrade deactivation logic."""

import logging

from common.apps.space.models import Space

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
    from django_tenants.utils import schema_context
    
    with schema_context(organization_slug):
        spaces = Space.objects.filter(
            is_deactivated=False
        ).order_by("created_at")
        total = spaces.count()
        excess_ids = list(
            spaces.values_list("id", flat=True)[max_spaces:]
        )
        count = (
            Space.objects.filter(id__in=excess_ids).update(
                is_deactivated=True
            )
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