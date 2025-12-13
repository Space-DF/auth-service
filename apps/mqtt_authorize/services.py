import logging
from typing import List, Tuple

from common.apps.space_role.models import SpaceRoleUser
from common.emqx import EMQXClient
from django.core.cache import cache
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken

from apps.mqtt_authorize.constants import (
    TOPIC_ENTITY_SPACE_REGEX,
    TOPIC_NONSPACE_REGEX,
    TOPIC_SPACE_REGEX,
)

logger = logging.getLogger(__name__)


def check_user_in_space(
    username: str, topic: str
) -> Tuple[str, str | None, str | None]:
    """
    Policy:
    - Topic does NOT have /space/<slug>/ -> allows ANY username (including anonymous)
    - Topic does HAVE /space/<slug>/ -> requires username to be a valid JWT and user belongs to that space
    - Entity topics (with /entity/) -> also requires user to belong to that space
    Returns tuple of (result, user_id or None, space_slug or None).
    """
    topic = (topic or "").strip("/")

    # Non-space topic: allow any user
    if TOPIC_NONSPACE_REGEX.match(topic):
        return "allow", None, None

    # Check space/device topics
    match = TOPIC_SPACE_REGEX.match(topic)
    if match:
        slug_name = match.group("space")
    else:
        # Check space/entity topics
        match = TOPIC_ENTITY_SPACE_REGEX.match(topic)
        if not match:
            return "deny", None, None
        slug_name = match.group("space")

    try:
        token = UntypedToken(username)
    except (TokenError, InvalidToken):
        return "deny", None, None

    payload = getattr(token, "payload", {})
    user_id = payload.get("user_id")
    if not user_id:
        return "deny", None, None

    # Check if user belongs to the space
    is_exists = SpaceRoleUser.objects.filter(
        organization_user_id=user_id,
        space_role__space__slug_name=slug_name,
    ).exists()

    return ("allow", str(user_id), slug_name) if is_exists else ("deny", None, None)


def save_client_id(
    result: str, user_id: str | None, space_slug: str | None, client_id: str
):
    if result == "allow" and user_id:
        cache_key = f"user_id:{user_id}_{space_slug}_client"  # noqa E231
        data = cache.get(cache_key) or {}
        client_ids: List[str] = data.get("client_ids", [])

        if client_id not in client_ids:
            client_ids.append(client_id)

        cache.set(cache_key, {"client_ids": client_ids}, timeout=60 * 60)


def disconnect_user_clients(user_id: str | None, space_slug: str | None):
    if not user_id:
        return

    cache_key = f"user_id:{user_id}_{space_slug}_client"  # noqa E231
    data = cache.get(cache_key) or {}
    client_ids: List[str] = data.get("client_ids", [])

    if not client_ids:
        return

    emqx_client = EMQXClient()

    for client_id in client_ids:
        try:
            emqx_client.disconnect_client(client_id)
        except Exception:  # noqa: BLE001
            logger.exception(
                "Failed to disconnect MQTT client %s for user %s", client_id, user_id
            )

    cache.delete(cache_key)
