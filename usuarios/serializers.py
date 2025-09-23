# usuarios/serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Residente
from condominio.serializers import PropiedadSerializer
from .common_serializers import UserSerializer # <-- 1. CAMBIA ESTA LÍNEA

class ResidenteSerializer(serializers.ModelSerializer):
    usuario = UserSerializer(read_only=True)
    propiedad = PropiedadSerializer(read_only=True)
    class Meta:
        model = Residente
        fields = ['id', 'usuario', 'propiedad', 'rol']

class RegistroSerializer(serializers.ModelSerializer):
    # ... (esta clase se queda igual) ...
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user