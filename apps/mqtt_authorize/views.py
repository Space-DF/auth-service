from common.utils.use_tenant_from_request import UseTenantFromRequestMixin
from rest_framework import generics, status
from rest_framework.response import Response

from apps.mqtt_authorize.serializers import MQTTAuthorizeSerializer
from apps.mqtt_authorize.services import check_user_in_space


class MQTTAuthorizeView(UseTenantFromRequestMixin, generics.GenericAPIView):
    serializer_class = MQTTAuthorizeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        topic = serializer.validated_data["topic"]
        username = serializer.validated_data["username"]

        result = check_user_in_space(username, topic)
        return Response({"result": result}, status=status.HTTP_200_OK)
