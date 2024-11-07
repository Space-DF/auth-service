from common.apps.space_role.models import SpacePolicy, SpaceRole
from django.db.models import Q


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
    owner_role = create_default_role_by_policy_tag(space, "Admin", [["administrator"]])
    reader_role = create_default_role_by_policy_tag(space, "Reader", [["read-only"]])
    create_default_role_by_policy_tag(
        space,
        "Editor",
        [
            ["dashboard", "full-access"],
            ["space-role", "read-only"],
            ["space-member", "read-only"],
        ],
    )

    return owner_role, reader_role
