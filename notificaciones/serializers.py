from rest_framework import serializers
from .models import DeviceToken

class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = ["id", "user", "token", "platform", "active", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at", "active"]

    token = serializers.CharField(max_length=255)
    platform = serializers.ChoiceField(choices=DeviceToken.PLATFORM_CHOICES)

    def create(self, validated_data):
        user = self.context["request"].user
        token = validated_data["token"]
        platform = validated_data["platform"]
        obj, _created = DeviceToken.objects.update_or_create(
            token=token,
            defaults={"user": user, "platform": platform, "active": True},
        )
        return obj

from rest_framework import serializers
from .models import Dispositivo # <-- Usa el nombre correcto

class DispositivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispositivo
        fields = ['token_dispositivo'] # Solo necesitamos el token del dispositivo