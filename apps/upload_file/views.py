from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.upload_file.service import get_presigned_url


class GetPresignedURL(APIView):
    def get(self, request):
        data = get_presigned_url(settings.AWS_S3.get("AWS_STORAGE_BUCKET_NAME"))
        if data is not None:
            return Response(data, status=status.HTTP_200_OK)

        return Response(
            {"error": "Get presigned url fail."}, status=status.HTTP_400_BAD_REQUEST
        )
