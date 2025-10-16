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
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auth_service.settings")
app = Celery("auth_service")
app.config_from_object("django.conf:settings", namespace="CELERY")

setup_organization_task_routing()
setup_synchronous_model_task_routing()

app.autodiscover_tasks(settings.CELERY_TASKS)

TASKS_AUTH = [
    constants.AUTH_SERVICE_OAUTH_CREDENTIALS_CREATION,
    constants.AUTH_SERVICE_ADD_OR_REMOVE_DEVICE,
]

existing = {queue.name: queue for queue in (app.conf.task_queues or ())}
routes = dict(app.conf.task_routes or {})

for name in TASKS_AUTH:
    if name not in existing:
        existing[name] = Queue(
            name,
            exchange=Exchange(name, type="direct"),
            routing_key=f"spacedf.tasks.{name}",
        )
    routes[f"spacedf.tasks.{name}"] = {
        "queue": name,
        "routing_key": f"spacedf.tasks.{name}",
    }

app.conf.task_queues = tuple(existing.values())
app.conf.task_routes = routes
