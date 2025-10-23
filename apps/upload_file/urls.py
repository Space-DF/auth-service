from django.urls import path

from apps.upload_file.views import GetPresignedURL, PostPresignedURL

urlpatterns = [
    path("presigned-url", PostPresignedURL.as_view(), name="presigned_url"),
    path(
        "presigned-url/<str:filename>",
        GetPresignedURL.as_view(),
        name="get_presigned_url",
    ),
]
