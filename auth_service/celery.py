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
    append_unique_task_queues,
    setup_organization_task_routing,
    setup_subscription_task_routing,
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
setup_subscription_task_routing(
    [
        {
            "task_name": "auth_downgrade",
            "service": "auth",
            "lifecycle": "downgrade",
        },
        {
            "task_name": "auth_upgrade",
            "service": "auth",
            "lifecycle": "upgrade",
        },
    ]
)

app.autodiscover_tasks(settings.CELERY_TASKS)

TASKS_AUTH = [
    constants.AUTH_SERVICE_OAUTH_CREDENTIALS_CREATION,
    constants.AUTH_SERVICE_ADD_OR_REMOVE_DEVICE,
    constants.AUTH_SERVICE_DELETE_UPLOAD_FILE,
]


routes = dict(app.conf.task_routes or {})
queues = []

for name in TASKS_AUTH:
    queues.append(
        Queue(
            name,
            exchange=Exchange(name, type="direct"),
            routing_key=f"spacedf.tasks.{name}",
        )
    )
    routes[f"spacedf.tasks.{name}"] = {
        "queue": name,
        "routing_key": f"spacedf.tasks.{name}",
    }

append_unique_task_queues(app, queues)
app.conf.task_routes = routes
