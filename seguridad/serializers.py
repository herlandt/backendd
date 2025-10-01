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

# Serializers para documentación
class ControlAccesoResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de control de acceso"""
    mensaje = serializers.CharField(help_text="Mensaje de respuesta")
    acceso_permitido = serializers.BooleanField(help_text="Si el acceso fue permitido")
    placa = serializers.CharField(help_text="Placa del vehículo")

class DashboardResumenResponseSerializer(serializers.Serializer):
    """Serializer para el resumen del dashboard"""
    visitas_hoy = serializers.IntegerField(help_text="Visitas de hoy")
    visitantes_activos = serializers.IntegerField(help_text="Visitantes actualmente en el condominio")
    eventos_mes = serializers.IntegerField(help_text="Eventos del mes")

class DashboardSeriesResponseSerializer(serializers.Serializer):
    """Serializer para series de datos del dashboard"""
    fechas = serializers.ListField(child=serializers.DateField(), help_text="Fechas")
    visitas = serializers.ListField(child=serializers.IntegerField(), help_text="Número de visitas por fecha")

class TopVisitantesResponseSerializer(serializers.Serializer):
    """Serializer para top visitantes"""
    visitante = serializers.CharField(help_text="Nombre del visitante")
    total_visitas = serializers.IntegerField(help_text="Total de visitas")

class SimpleOperationResponseSerializer(serializers.Serializer):
    """Serializer para operaciones simples"""
    mensaje = serializers.CharField(help_text="Mensaje de respuesta")
    success = serializers.BooleanField(default=True, help_text="Estado de la operación")