fromclass PropiedadViewSet(viewsets.ModelViewSet):
    queryset = Propiedad.objects.all().order_by('numero_casa')
    serializer_class = PropiedadSerializer
    # Filtros avanzados
    filterset_fields = {
        'numero_casa': ['exact', 'icontains'],
        'metros_cuadrados': ['gte', 'lte'],
        'propietario': ['exact'],
    }
    search_fields = ['numero_casa']
    ordering_fields = ['numero_casa', 'metros_cuadrados']
    ordering = ['numero_casa']k import viewsets
from .models import Propiedad, AreaComun, Aviso
from .serializers import PropiedadSerializer, AreaComunSerializer, AvisoSerializer

class PropiedadViewSet(viewsets.ModelViewSet):
    queryset = Propiedad.objects.all().order_by('numero_casa')
    serializer_class = PropiedadSerializer
    # Filtros avanzados
    filterset_fields = {
        'numero': ['exact', 'icontains'],
        'tipo': ['exact'],
        'metros_cuadrados': ['gte', 'lte'],
        'habitaciones': ['exact', 'gte', 'lte'],
        'banos': ['exact', 'gte', 'lte'],
    }
    search_fields = ['numero', 'tipo']
    ordering_fields = ['numero', 'metros_cuadrados', 'habitaciones']
    ordering = ['numero']

class AreaComunViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AreaComun.objects.all()
    serializer_class = AreaComunSerializer
    # Filtros avanzados
    filterset_fields = {
        'nombre': ['icontains'],
        'capacidad': ['gte', 'lte', 'exact'],
        'costo_reserva': ['gte', 'lte', 'exact'],
    }
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'capacidad', 'costo_reserva']
    ordering = ['nombre']


# --- AÑADE ESTA CLASE ---
class AvisoViewSet(viewsets.ModelViewSet):
    queryset = Aviso.objects.all()
    serializer_class = AvisoSerializer
    # Filtros avanzados
    filterset_fields = {
        'titulo': ['icontains'],
        'fecha_creacion': ['gte', 'lte', 'exact'],
        'autor': ['exact'],
        'importante': ['exact'],
    }
    search_fields = ['titulo', 'contenido', 'autor__username']
    ordering_fields = ['fecha_creacion', 'titulo']
    ordering = ['-fecha_creacion']

from rest_framework import viewsets, permissions
from .models import Propiedad, AreaComun, Aviso, Regla # Añade Regla
from .serializers import PropiedadSerializer, AreaComunSerializer, AvisoSerializer, ReglaSerializer # Añade ReglaSerializer

# ... (tus otros ViewSets existentes)

class ReglaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint de API para visualizar las reglas del condominio.
    Es de solo lectura. Las reglas se gestionan desde el panel de administrador.
    """
    queryset = Regla.objects.filter(activa=True)
    # Filtros avanzados
    filterset_fields = {
        'categoria': ['exact'],
        'activa': ['exact'],
        'fecha_vigencia': ['gte', 'lte', 'exact'],
    }
    search_fields = ['titulo', 'descripcion', 'categoria']
    ordering_fields = ['fecha_vigencia', 'titulo', 'categoria']
    ordering = ['categoria', 'titulo']
    serializer_class = ReglaSerializer
    permission_classes = [permissions.IsAuthenticated] # Solo usuarios autenticados pueden ver las reglas