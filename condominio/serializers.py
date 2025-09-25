# condominio/serializers.py

# condominio/serializers.py
from rest_framework import serializers
from .models import Aviso, Propiedad, AreaComun
# ¡CAMBIO 3! Apuntamos al nuevo fichero común.
from usuarios.common_serializers import UserReadSerializer

class PropiedadSerializer(serializers.ModelSerializer):
    propietario = UserReadSerializer(read_only=True)
    class Meta:
        model = Propiedad
        fields = ['id', 'numero_casa', 'propietario', 'metros_cuadrados']

# ... (El resto del fichero se queda igual) ...
class AreaComunSerializer(serializers.ModelSerializer):
    # ... (esta clase se queda igual) ...
    class Meta:
        model = AreaComun
        fields = ['id', 'nombre', 'descripcion', 'capacidad', 'costo_reserva', 'horario_apertura', 'horario_cierre']

class AvisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aviso
        fields = '__all__'