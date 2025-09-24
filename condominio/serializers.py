# condominio/serializers.py

from rest_framework import serializers
from .models import Aviso, Propiedad, AreaComun
from usuarios.common_serializers import UserSerializer # <-- 2. CAMBIA ESTA LÍNEA

class PropiedadSerializer(serializers.ModelSerializer):
    propietario = UserSerializer(read_only=True)
    class Meta:
        model = Propiedad
        fields = ['id', 'numero_casa', 'propietario', 'metros_cuadrados']

class AreaComunSerializer(serializers.ModelSerializer):
    # ... (esta clase se queda igual) ...
    class Meta:
        model = AreaComun
        fields = ['id', 'nombre', 'descripcion', 'capacidad', 'costo_reserva', 'horario_apertura', 'horario_cierre']

class AvisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aviso
        fields = '__all__'