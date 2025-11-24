from rest_framework import serializers


class MQTTAuthorizeSerializer(serializers.Serializer):
    username = serializers.CharField()
    topic = serializers.CharField()
    client_id = serializers.CharField()
