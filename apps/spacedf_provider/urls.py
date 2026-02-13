from django.urls import path

from .views import SpaceDFConsoleLoginView

urlpatterns = [
    path("spacedf-console", SpaceDFConsoleLoginView.as_view(), name="spacedf_login"),
]
