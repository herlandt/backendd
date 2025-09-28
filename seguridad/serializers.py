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

# seguridad/views.py
from rest_framework import generics, permissions
from seguridad.models import Deteccion
from .serializers import DeteccionSerializer

class DeteccionListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DeteccionSerializer

    def get_queryset(self):
        qs = Deteccion.objects.all()
        cam = self.request.query_params.get("camera")
        if cam:
            qs = qs.filter(camera__name=cam)
        return qs
