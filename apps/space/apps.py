from django.apps import AppConfig


class AuthSpaceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.space"
    label = "auth_space"

    def ready(self):
        from . import signals  # noqa: F401
