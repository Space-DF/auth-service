from common.apps.space_role.models import SpaceRoleUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken

from apps.mqtt_authorize.constants import TOPIC_NONSPACE_REGEX, TOPIC_SPACE_REGEX


def check_user_in_space(username: str, topic: str) -> str:
    """
    Policy:
    - Topic does NOT have /space/<slug>/ -> allows ANY username (including anonymous)
    - Topic does HAVE /space/<slug>/ -> requires username to be a valid JWT and user belongs to that space
    """
    topic = (topic or "").strip("/")

    if TOPIC_NONSPACE_REGEX.match(topic):
        return "allow"

    match = TOPIC_SPACE_REGEX.match(topic)
    if not match:
        return "deny"

    try:
        token = UntypedToken(username)
    except (TokenError, InvalidToken):
        return "deny"

    payload = getattr(token, "payload", {})
    user_id = payload.get("user_id")
    if not user_id:
        return "deny"

    slug_name = match.group("space")

    is_exists = SpaceRoleUser.objects.filter(
        organization_user_id=user_id,
        space_role__space__slug_name=slug_name,
    ).exists()

    return "allow" if is_exists else "deny"
