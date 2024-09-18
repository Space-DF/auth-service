from operator import itemgetter

from allauth.socialaccount.models import SocialApp
from common.celery import constants
from common.celery.tasks import task
from django.db import transaction
from django.db.utils import ProgrammingError
from django_tenants.utils import schema_context

from spacedf_provider.provider import SpaceDFProvider


@task(
    name=f"spacedf.tasks.{constants.AUTH_SERVICE_OAUTH_CREDENTIALS_CREATION}",
    autoretry_for=(ProgrammingError,),
)
@transaction.atomic
def oauth_credentials_creation(**kwargs):
    slug_name, client_secret, client_id = itemgetter(
        "slug_name", "client_secret", "client_id"
    )(kwargs)
    with schema_context(slug_name):
        oauth_credentials = SocialApp(
            provider=SpaceDFProvider.id,
            provider_id=SpaceDFProvider.id,
            name=SpaceDFProvider.name,
            client_id=client_id,
            secret=client_secret,
        )
        oauth_credentials.save()
