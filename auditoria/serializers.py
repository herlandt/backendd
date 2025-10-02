# auditoria/serializers.py
from rest_framework import serializers
from .models import Bitacora
from django.contrib.auth.models import User

class UsuarioSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple para mostrar info básica del usuario"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class BitacoraSerializer(serializers.ModelSerializer):
    """Serializer para mostrar registros de auditoría"""
    usuario = UsuarioSimpleSerializer(read_only=True)
    timestamp_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = Bitacora
        fields = ['id', 'timestamp', 'timestamp_formatted', 'usuario', 'ip_address', 'accion', 'descripcion']
        read_only_fields = ['id', 'timestamp', 'usuario', 'ip_address', 'accion', 'descripcion']
    
    def get_timestamp_formatted(self, obj):
        """Formato de fecha más legible"""
        return obj.timestamp.strftime('%Y-%m-%d %H:%M:%S') if obj.timestamp else None