import logging
import uuid

import boto3
from django.conf import settings


class S3Service:
    def __init__(self):
        try:
            self.client = boto3.client("s3")
            self.bucket_name = settings.AWS_S3.get("AWS_STORAGE_BUCKET_NAME")
        except Exception as e:
            logging.error(f"Error: {e}")
            self.client = None

    def get_presigned_url(self, expiration=3600):
        """
        return presigned URL and file name
        """
        if not self.client:
            logging.error("S3 client is not initialized.")
            return None

        try:
            file_name = uuid.uuid4()
            presigned_url = self.client.generate_presigned_url(
                ClientMethod="put_object",
                Params={"Bucket": self.bucket_name, "Key": f"uploads/{file_name}.png"},
                ExpiresIn=expiration,
                HttpMethod="PUT",
            )
            return {"file_name": file_name, "presigned_url": presigned_url}
        except Exception as e:
            logging.error(f"Error: {e}")
            return None

    def get_url(self, file_name):
        """
        Return the URL from name file
        """
        region = settings.AWS_S3.get('AWS_REGION')
        return f"https://{self.bucket_name}.s3.{region}.amazonaws.com/uploads/{file_name}.png"
