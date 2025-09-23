from rest_framework import serializers
from .models import Visitante, Visita, Vehiculo

class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = ['id', 'propiedad', 'placa', 'marca', 'modelo']

class VisitanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitante
        fields = ['id', 'nombre_completo', 'documento_identidad']

class VisitaSerializer(serializers.ModelSerializer):
    visitante = VisitanteSerializer()
    propiedad = serializers.ReadOnlyField(source='propiedad.numero_casa')
    class Meta:
        model = Visita
        fields = ['id', 'propiedad', 'visitante', 'fecha_ingreso_programado', 'fecha_salida_programada']

    def create(self, validated_data):
        visitante_data = validated_data.pop('visitante')
        visitante, created = Visitante.objects.get_or_create(
            documento_identidad=visitante_data['documento_identidad'],
            defaults={'nombre_completo': visitante_data['nombre_completo']}
        )
        visita = Visita.objects.create(visitante=visitante, **validated_data)
        return visita