from django.urls import path

from apps.mqtt_authorize.views import MQTTAuthorizeView

app_name = "mqtt_authorize"

urlpatterns = [
    path("mqtt/authorize", MQTTAuthorizeView.as_view(), name="authorize"),
]
