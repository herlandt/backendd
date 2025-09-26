from rest_framework import serializers
from .models import Visitante, Visita, Vehiculo


class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = ['id', 'propiedad', 'visitante', 'placa', 'marca', 'modelo']


class VisitanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitante
        fields = ['id', 'nombre_completo', 'documento_identidad']


class VisitaSerializer(serializers.ModelSerializer):
    # Visitante anidado para crear/usar visitante automáticamente
    visitante = VisitanteSerializer()

    # Propiedad se muestra como texto (read-only); la elegimos en la vista
    propiedad = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Visita
        fields = [
            'id',
            'propiedad',
            'visitante',
            'fecha_ingreso_programado',
            'fecha_salida_programada',
            'ingreso_real',
            'salida_real',
        ]
        read_only_fields = ['ingreso_real', 'salida_real']

    def create(self, validated_data):
        visitante_data = validated_data.pop('visitante')
        visitante, _ = Visitante.objects.get_or_create(
            documento_identidad=visitante_data['documento_identidad'],
            defaults={'nombre_completo': visitante_data.get('nombre_completo', '')},
        )
        # Si viene un nombre distinto y no es vacío, lo actualizamos
        nombre = visitante_data.get('nombre_completo')
        if nombre:
            visitante.nombre_completo = nombre
            visitante.save(update_fields=['nombre_completo'])

        return Visita.objects.create(visitante=visitante, **validated_data)
