from operator import itemgetter

from common.apps.space.models import Space
from common.celery import constants
from common.celery.tasks import task
from django.db import transaction
from django.db.models import BooleanField, Case, F, IntegerField, Value, When
from django.db.models.functions import Greatest
from django.db.utils import ProgrammingError
from django_tenants.utils import schema_context

from apps.space.consumers import deactivate_excess_spaces, reactivate_spaces


@task(
    name="spacedf.tasks.space_downgrade",
    autoretry_for=(Exception,),
    retry_backoff=2,
    max_retries=3,
)
def space_downgrade_task(**kwargs):
    return deactivate_excess_spaces(kwargs["org_slug"], kwargs.get("limits"))


@task(
    name="spacedf.tasks.space_upgrade",
    autoretry_for=(Exception,),
    retry_backoff=2,
    max_retries=3,
)
def space_upgrade_task(**kwargs):
    return reactivate_spaces(kwargs["org_slug"])


# TODO: need function on device service call this task
@task(
    name=f"spacedf.tasks.{constants.AUTH_SERVICE_ADD_OR_REMOVE_DEVICE}",
    autoretry_for=(ProgrammingError,),
    retry_backoff=2,
    max_retries=3,
)
@transaction.atomic
def add_or_remove_device(**kwargs):
    slug_name, space_slug_name, action_type = itemgetter(
        "slug_name", "space_slug_name", "type"
    )(kwargs)
    with schema_context(slug_name):
        value = Case(
            When(
                Value(action_type == "add", output_field=BooleanField()), then=Value(1)
            ),
            When(
                Value(action_type == "remove", output_field=BooleanField()),
                then=Value(-1),
            ),
            default=Value(0),
            output_field=IntegerField(),
        )

        Space.objects.filter(slug_name=space_slug_name).update(
            total_devices=Greatest(F("total_devices") + value, Value(0)),
        )
