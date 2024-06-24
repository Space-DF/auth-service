from django.contrib import admin
from space_role.models import Policy, SpaceRole


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "description",
        "tags",
        "actions",
        "created_at",
        "updated_at",
    )


@admin.register(SpaceRole)
class SpaceRoleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "space",
        "created_at",
        "updated_at",
    )
