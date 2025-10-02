# condominio/serializers.py

from rest_framework import serializers
from .models import Aviso, Propiedad, AreaComun, Regla, LecturaAviso
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
    total_lecturas = serializers.ReadOnlyField()
    porcentaje_lectura = serializers.ReadOnlyField()
    total_residentes_objetivo = serializers.ReadOnlyField()
    
    class Meta:
        model = Aviso
        fields = [
            'id', 'titulo', 'contenido', 'fecha_publicacion', 
            'activo', 'dirigido_a', 'total_lecturas', 
            'porcentaje_lectura', 'total_residentes_objetivo'
        ]

class LecturaAvisoSerializer(serializers.ModelSerializer):
    residente_info = serializers.SerializerMethodField()
    aviso_titulo = serializers.CharField(source='aviso.titulo', read_only=True)
    
    class Meta:
        model = LecturaAviso
        fields = [
            'id', 'aviso', 'aviso_titulo', 'residente', 
            'residente_info', 'fecha_lectura', 'ip_lectura'
        ]
        read_only_fields = ['fecha_lectura']
    
    def get_residente_info(self, obj):
        """Retorna información del residente que leyó el aviso"""
        return {
            'id': obj.residente.id,
            'username': obj.residente.usuario.username,
            'email': obj.residente.usuario.email,
            'nombre_completo': f"{obj.residente.usuario.first_name} {obj.residente.usuario.last_name}".strip(),
            'rol': obj.residente.rol,
            'propiedad': obj.residente.propiedad.numero_casa if obj.residente.propiedad else None
        }

class AvisoDetalleSerializer(serializers.ModelSerializer):
    """Serializer detallado con información de lecturas"""
    lecturas = LecturaAvisoSerializer(many=True, read_only=True)
    total_lecturas = serializers.ReadOnlyField()
    porcentaje_lectura = serializers.ReadOnlyField()
    total_residentes_objetivo = serializers.ReadOnlyField()
    residentes_sin_leer = serializers.SerializerMethodField()
    
    class Meta:
        model = Aviso
        fields = [
            'id', 'titulo', 'contenido', 'fecha_publicacion', 
            'activo', 'dirigido_a', 'total_lecturas', 
            'porcentaje_lectura', 'total_residentes_objetivo',
            'lecturas', 'residentes_sin_leer'
        ]
    
    def get_residentes_sin_leer(self, obj):
        """Retorna lista de residentes que NO han leído el aviso"""
        from usuarios.models import Residente
        
        # Obtener todos los residentes objetivo
        if obj.dirigido_a == 'TODOS':
            residentes_objetivo = Residente.objects.all()
        elif obj.dirigido_a == 'PROPIETARIOS':
            residentes_objetivo = Residente.objects.filter(rol='propietario')
        elif obj.dirigido_a == 'INQUILINOS':
            residentes_objetivo = Residente.objects.filter(rol='inquilino')
        else:
            residentes_objetivo = Residente.objects.none()
        
        # Obtener residentes que YA leyeron
        residentes_que_leyeron = obj.lecturas.values_list('residente_id', flat=True)
        
        # Filtrar residentes que NO han leído
        residentes_sin_leer = residentes_objetivo.exclude(id__in=residentes_que_leyeron)
        
        return [
            {
                'id': r.id,
                'username': r.usuario.username,
                'email': r.usuario.email,
                'nombre_completo': f"{r.usuario.first_name} {r.usuario.last_name}".strip(),
                'rol': r.rol,
                'propiedad': r.propiedad.numero_casa if r.propiedad else None
            }
            for r in residentes_sin_leer.select_related('usuario', 'propiedad')
        ]

from rest_framework import serializers
from .models import Propiedad, AreaComun, Aviso, Regla # Añade Regla aquí

# ... (tus otros serializers existentes)

class ReglaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regla
        fields = ['codigo', 'titulo', 'descripcion', 'categoria']