from django.conf import settings
import boto3
import uuid

class S3Service:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_S3.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=settings.AWS_S3.get("AWS_SECRET_ACCESS_KEY_ID"),
            region_name=settings.AWS_S3.get("AWS_REGION"),
        )
        self.bucket_name = settings.AWS_S3.get("AWS_STORAGE_BUCKET_NAME")

    def upload_file(self, file):
        """
        Upload file to S3
        """
        file_extension = file.name.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_extension}"

        self.client.upload_fileobj(
            file,
            self.bucket_name,
            f"uploads/{file_name}",
        )
        return file_name

    def get_url(self, file_name):
        """
        Return the URL from name file
        """
        return f"https://{self.bucket_name}.s3.{settings.AWS_S3.get('AWS_REGION')}.amazonaws.com/uploads/{file_name}"
