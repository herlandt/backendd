from rest_framework import serializers
from .models import Visitante, Vehiculo, Visita


# Para los POST de control de acceso/salida
class ConsultaPlacaSerializer(serializers.Serializer):
    placa = serializers.CharField(max_length=20)


# CRUD
class VisitanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitante
        fields = ["id", "nombre_completo", "documento", "telefono", "email"]


class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = ["id", "placa", "propiedad", "visitante"]


class VisitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visita
        fields = [
            "id",
            "visitante",
            "propiedad",
            "fecha_ingreso_programado",
            "fecha_salida_programada",
            "ingreso_real",
            "salida_real",
        ]
