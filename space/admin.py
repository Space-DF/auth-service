from django.contrib import admin
from space.models import Space


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "logo",
        "is_multi_tenant",
        "created_at",
        "updated_at",
    )
