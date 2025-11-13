from rest_framework import serializers


class MQTTAuthorizeSerializer(serializers.Serializer):
    username = serializers.CharField()
    topic = serializers.CharField()
