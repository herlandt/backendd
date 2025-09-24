from rest_framework import serializers
from .models import PersonalMantenimiento, SolicitudMantenimiento
from .models import Mantenimiento
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

class MantenimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mantenimiento
        fields = '__all__'
        read_only_fields = ('estado', 'fecha_solicitud', 'fecha_finalizacion', 'personal_mantenimiento')