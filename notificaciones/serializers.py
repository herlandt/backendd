from rest_framework import serializers
from .models import DeviceToken, Dispositivo

class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DeviceToken
        fields = ["id", "token", "platform", "user", "active", "created_at", "updated_at"]
        read_only_fields = ["user", "created_at", "updated_at"]

    # nos aseguramos de asociar el token al usuario autenticado y no duplicarlo
    def create(self, validated_data):
        request = self.context.get("request")
        user    = getattr(request, "user", None)
        token   = validated_data["token"]
        platform= validated_data["platform"]
        obj, _  = DeviceToken.objects.update_or_create(
            token=token,
            defaults={"user": user, "platform": platform, "active": True},
        )
        return obj


class DispositivoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Dispositivo
        fields = ["id", "token_dispositivo", "activo", "fecha_creacion"]
        read_only_fields = ["activo", "fecha_creacion"]
