from common.apps.upload_file.service import delete_file
from common.celery import constants
from common.celery.tasks import task


@task(name=f"spacedf.tasks.{constants.AUTH_SERVICE_DELETE_UPLOAD_FILE}")
def delete_upload_file(**kwargs):
    delete_file(
        kwargs["bucket_name"],
        kwargs["link_file"],
    )
