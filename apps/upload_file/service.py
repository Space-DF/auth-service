import logging
import uuid

import boto3

client = boto3.client("s3")


def get_presigned_url(bucket_name, expiration=3600):
    """
    return presigned URL and file name
    """
    try:
        file_name = uuid.uuid4()
        presigned_url = client.generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": bucket_name, "Key": f"uploads/{file_name}.png"},
            ExpiresIn=expiration,
            HttpMethod="PUT",
        )
        return {"file_name": file_name, "presigned_url": presigned_url}
    except Exception as e:
        logging.error(f"Error: {e}")
        return None


def get_url(bucket_name, region, file_name):
    """
    Return the URL from name file
    """
    return f"https://{bucket_name}.s3.{region}.amazonaws.com/uploads/{file_name}.png"
