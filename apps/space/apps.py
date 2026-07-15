import threading

from django.apps import AppConfig

_DOWNGRADE_STARTED = False


class AuthSpaceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.space"
    label = "auth_space"

    def ready(self):
        from . import signals  # noqa: F401

        _start_downgrade_consumer()


def _start_downgrade_consumer():
    global _DOWNGRADE_STARTED
    if _DOWNGRADE_STARTED:
        return

    def _run():
        from common.utils.downgrade_consumer import run_downgrade_consumer

        from apps.space.consumers import deactivate_excess_spaces

        run_downgrade_consumer(
            queue_name="auth.org.events.queue",
            callback=deactivate_excess_spaces,
        )

    thread = threading.Thread(target=_run, name="SpaceDowngradeConsumer", daemon=True)
    thread.start()
    _DOWNGRADE_STARTED = True
