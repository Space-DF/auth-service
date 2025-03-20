from django.urls import path

from apps.presigned_url.views import GetPresignedURL

urlpatterns = [
    path("presigned-url", GetPresignedURL.as_view(), name="presigned_url"),
]
