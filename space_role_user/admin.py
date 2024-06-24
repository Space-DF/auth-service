from django.contrib import admin
from space_role_user.models import SpaceRoleUser


@admin.register(SpaceRoleUser)
class SpaceRoleUserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "space_role",
        "organization_user",
        "created_at",
        "updated_at",
    )
