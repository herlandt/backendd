from rest_framework import serializers
from .models import DeviceToken, Dispositivo

class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = ["id", "token", "platform", "user", "active", "created_at", "updated_at"]
        read_only_fields = ["user", "created_at", "updated_at"]

class DispositivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispositivo
        fields = ["token_dispositivo"]
