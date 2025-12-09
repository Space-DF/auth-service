from common.utils.switch_tenant import UseTenantFromRequestMixin
from rest_framework import generics, status
from rest_framework.response import Response

from apps.mqtt_authorize.serializers import MQTTAuthorizeSerializer
from apps.mqtt_authorize.services import check_user_in_space, save_client_id


class MQTTAuthorizeView(UseTenantFromRequestMixin, generics.GenericAPIView):
    serializer_class = MQTTAuthorizeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        topic = serializer.validated_data["topic"]
        username = serializer.validated_data["username"]
        client_id = serializer.validated_data["client_id"]

        result, user_id, space_slug = check_user_in_space(username, topic)

        save_client_id(result, user_id, space_slug, client_id)
        return Response({"result": result}, status=status.HTTP_200_OK)
