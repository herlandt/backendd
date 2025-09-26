from rest_framework import serializers
from .models import Visitante, Visita, Vehiculo
from condominio.models import Propiedad

class VisitanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitante
        fields = ['id', 'nombre_completo', 'documento_identidad']

class VisitaSerializer(serializers.ModelSerializer):
    visitante = VisitanteSerializer()
    propiedad = serializers.StringRelatedField(read_only=True)
    # Guardias podrán enviar propiedad_id; mapeamos al FK real con source='propiedad'
    propiedad_id = serializers.PrimaryKeyRelatedField(
        queryset=Propiedad.objects.all(), write_only=True, required=False, source='propiedad'
    )
    # Estado calculado para la lista/detalle
    estado = serializers.SerializerMethodField()

    class Meta:
        model = Visita
        fields = [
            'id', 'propiedad', 'propiedad_id', 'visitante',
            'fecha_ingreso_programado', 'fecha_salida_programada',
            'ingreso_real', 'salida_real', 'estado'
        ]
        read_only_fields = ['ingreso_real', 'salida_real']

    def get_estado(self, obj):
        if obj.salida_real:
            return 'FINALIZADA'
        if obj.ingreso_real:
            return 'EN_CURSO'
        return 'PROGRAMADA'

    def create(self, validated_data):
        visitante_data = validated_data.pop('visitante')
        visitante, _ = Visitante.objects.get_or_create(
            documento_identidad=visitante_data['documento_identidad'],
            defaults={'nombre_completo': visitante_data['nombre_completo']}
        )
        return Visita.objects.create(visitante=visitante, **validated_data)

class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = ['id', 'propiedad', 'visitante', 'placa', 'marca', 'modelo']
