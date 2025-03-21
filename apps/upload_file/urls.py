from django.urls import path

from apps.upload_file.views import GetPresignedURL

urlpatterns = [
    path("presigned-url", GetPresignedURL.as_view(), name="presigned_url"),
]
