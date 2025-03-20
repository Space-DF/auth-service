from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_service.s3_service import S3Service


class GetPresignedURL(APIView):

    def get(self, request):
        s3_service = S3Service()
        data = s3_service.get_presigned_url()
        if data is not None:
            return Response(data, status=status.HTTP_200_OK)

        return Response(
            {"error": "Get presigned url fail."}, status=status.HTTP_400_BAD_REQUEST
        )
