from django.apps import AppConfig


class AuthSpaceRoleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.space_role"
    label = "auth_space_role"

    def ready(self):
        from . import signals  # noqa: F401
