from rest_framework import serializers
from .models import PersonalMantenimiento, SolicitudMantenimiento

class PersonalMantenimientoSerializer(serializers.ModelSerializer):
    usuario = serializers.ReadOnlyField(source='usuario.username')
    class Meta:
        model = PersonalMantenimiento
        fields = ['id', 'usuario', 'especialidad']

class SolicitudMantenimientoSerializer(serializers.ModelSerializer):
    solicitado_por = serializers.ReadOnlyField(source='solicitado_por.username')
    propiedad_numero = serializers.ReadOnlyField(source='propiedad.numero_casa')
    class Meta:
        model = SolicitudMantenimiento
        fields = ['id', 'solicitado_por', 'propiedad_numero', 'titulo', 'descripcion', 'estado', 'fecha_creacion', 'asignado_a']