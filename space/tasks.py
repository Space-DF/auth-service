from operator import itemgetter

from common.apps.space.models import Space
from common.celery import constants
from common.celery.tasks import task
from django.db import transaction
from django.db.models import Case, F, When
from django.db.utils import ProgrammingError
from django_tenants.utils import schema_context


# TODO: need function on device service call this task
@task(
    name=f"spacedf.tasks.{constants.AUTH_SERVICE_ADD_OR_REMOVE_DEVICE}",
    autoretry_for=(ProgrammingError,),
)
@transaction.atomic
def add_or_remove_device(**kwargs):
    slug_name, space_slug_name, action_type = itemgetter(
        "slug_name", "space_slug_name", "type"
    )(kwargs)
    with schema_context(slug_name):
        Space.objects.filter(slug_name=space_slug_name).update(
            total_devices=Case(
                When(condition=(action_type == "add"), then=F("total_devices") + 1),
                When(condition=(action_type == "remove"), then=F("total_devices") - 1),
                default=F("total_devices"),
            )
        )
