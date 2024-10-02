import importlib.util
import os
import sys

from kombu import Exchange, Queue

if importlib.util.find_spec("common") is None:
    sys.path.append(
        os.path.abspath(os.path.join("..", "django-common-utils"))
    )  # Import django-common-utils without install

from celery import Celery
from common.celery import constants  # noqa
from common.celery.routing import (
    setup_organization_task_routing,
    setup_synchronous_model_task_routing,
)
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auth_service.settings.local")
app = Celery("auth_service")
app.config_from_object("django.conf:settings", namespace="CELERY")

setup_organization_task_routing()
setup_synchronous_model_task_routing()

app.autodiscover_tasks(settings.CELERY_TASKS)
app.conf.task_queues = app.conf.task_queues + (
    Queue(
        constants.AUTH_SERVICE_OAUTH_CREDENTIALS_CREATION,
        exchange=Exchange(
            constants.AUTH_SERVICE_OAUTH_CREDENTIALS_CREATION, type="direct"
        ),
        routing_key=f"spacedf.tasks.{constants.AUTH_SERVICE_OAUTH_CREDENTIALS_CREATION}",
    ),
)
app.conf.task_routes[
    f"spacedf.tasks.{constants.AUTH_SERVICE_OAUTH_CREDENTIALS_CREATION}"
] = {
    "queue": constants.AUTH_SERVICE_OAUTH_CREDENTIALS_CREATION,
    "routing_key": f"spacedf.tasks.{constants.AUTH_SERVICE_OAUTH_CREDENTIALS_CREATION}",
}
