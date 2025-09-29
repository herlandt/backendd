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


# seguridad/serializers.py
from rest_framework import serializers
from seguridad.models import Deteccion

class DeteccionSerializer(serializers.ModelSerializer):
    camera = serializers.CharField(source="camera.name")
    matched_username = serializers.CharField(source="matched_user.username", allow_null=True)
    class Meta:
        model = Deteccion
        fields = ["id","camera","matched_username","similarity","face_id","ts","frame","raw"]

# al final de seguridad/serializers.py

from .models import EventoSeguridad # Asegúrate de importar el modelo

# ... tus otros serializadores (VisitanteSerializer, VehiculoSerializer, etc.)

# --- AÑADE ESTA CLASE ---
class EventoSeguridadSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventoSeguridad
        fields = '__all__'