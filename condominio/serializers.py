# condominio/serializers.py

from rest_framework import serializers
from .models import Aviso, Propiedad, AreaComun, Regla
from usuarios.common_serializers import UserReadSerializer
from django.contrib.auth.models import User 
from usuarios.common_serializers import UserReadSerializer


class PropiedadSerializer(serializers.ModelSerializer):
    # Para mostrar el propietario de forma legible (GET)
    propietario = UserReadSerializer(read_only=True)
    # Para recibir el ID del propietario al crear (POST)
    propietario_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='propietario', write_only=True
    )

    class Meta:
        model = Propiedad
        # Añadimos 'propietario_id' a la lista de campos
        fields = ['id', 'numero_casa', 'propietario', 'metros_cuadrados', 'propietario_id']
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

from rest_framework import serializers
from .models import Propiedad, AreaComun, Aviso, Regla # Añade Regla aquí

# ... (tus otros serializers existentes)

class ReglaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regla
        fields = ['codigo', 'titulo', 'descripcion', 'categoria']