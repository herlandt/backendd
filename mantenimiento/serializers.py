from rest_framework import serializers
from .models import SolicitudMantenimiento

# Este es el único serializador que debe estar en este archivo.
# Se han eliminado las importaciones y clases que causaban el error.

class SolicitudMantenimientoSerializer(serializers.ModelSerializer):
    solicitado_por = serializers.StringRelatedField(read_only=True)
    propiedad_numero = serializers.StringRelatedField(source='propiedad.numero_casa', read_only=True)
    # Hacemos que el campo 'asignado_a' muestre el nombre de usuario
    asignado_a = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SolicitudMantenimiento
        fields = [
            'id',
            'solicitado_por',
            'propiedad_numero',
            'titulo',
            'descripcion',
            'estado',
            'fecha_creacion',
            'asignado_a'
        ]