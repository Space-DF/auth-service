from common.apps.refresh_tokens.services import create_jwt_tokens
from common.apps.space_role.models import SpacePolicy


def create_space_access_token(space_slug_name, user_id, access_token):
    policies = SpacePolicy.objects.filter(
        spacerole__space__slug_name=space_slug_name,
        spacerole__space_role_user__organization_user_id=user_id,
    ).distinct()
    access_token["permissions"] = list(
        set(
            [
                policy_permission
                for policy in policies
                for policy_permission in policy.permissions
            ]
        )
    )
    access_token["space"] = space_slug_name
    return access_token


def create_space_jwt_tokens(user, space_slug, issuer=None, **kwargs):
    refresh_token, access_token = create_jwt_tokens(user, issuer, **kwargs)

    if space_slug:
        access_token = create_space_access_token(space_slug, user.id, access_token)
    return refresh_token, access_token
