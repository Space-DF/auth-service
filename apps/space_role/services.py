from common.apps.space_role.models import SpacePolicy, SpaceRole
from django.core.cache import cache
from django.db.models import Q

from apps.space_role.constants import SpaceRoleType


def create_default_role_by_policy_tag(space, name, tags):
    q_filter = Q()
    for tag in tags:
        q_filter |= Q(tags__contains=tag)
    policies = SpacePolicy.objects.filter(q_filter).all()
    space_role = SpaceRole(name=name, space=space)
    space_role.save()
    space_role.policies.set([policy.pk for policy in policies])
    space_role.save()
    return space_role


def create_space_default_role(space):
    owner_role = create_default_role_by_policy_tag(
        space, SpaceRoleType.ADMIN_ROLE, [["administrator"]]
    )
    viewer_role = create_default_role_by_policy_tag(
        space, SpaceRoleType.VIEWER_ROLE, [["read-only"]]
    )
    create_default_role_by_policy_tag(
        space,
        SpaceRoleType.EDITOR_ROLE,
        [
            ["dashboard", "full-access"],
            ["space-role", "read-only"],
            ["space-member", "read-only"],
        ],
    )

    return owner_role, viewer_role


def clear_user_permission_cache(user_id):
    if user_id:
        cache_key = f"space_permissions_{user_id}"
        if cache.get(cache_key):
            cache.delete(cache_key)
