from rest_framework import viewsets
from .models import Propiedad, AreaComun, Aviso, Regla
from .serializers import PropiedadSerializer, AreaComunSerializer, AvisoSerializer, ReglaSerializer

class PropiedadViewSet(viewsets.ModelViewSet):
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
    ordering = ['numero_casa']

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

class AvisoViewSet(viewsets.ModelViewSet):
    queryset = Aviso.objects.all()
    serializer_class = AvisoSerializer
    # Filtros avanzados
    filterset_fields = {
        'titulo': ['icontains'],
        'fecha_publicacion': ['gte', 'lte', 'exact'],
    }
    search_fields = ['titulo', 'contenido']
    ordering_fields = ['fecha_publicacion', 'titulo']
    ordering = ['-fecha_publicacion']

class ReglaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint de API para visualizar las reglas del condominio.
    Es de solo lectura. Las reglas se gestionan desde el panel de administrador.
    """
    queryset = Regla.objects.filter(activa=True)
    serializer_class = ReglaSerializer
    # Filtros avanzados
    filterset_fields = {
        'categoria': ['exact'],
        'activa': ['exact'],
        'codigo': ['exact', 'icontains'],
    }
    search_fields = ['titulo', 'descripcion', 'categoria', 'codigo']
    ordering_fields = ['categoria', 'titulo', 'codigo']
    ordering = ['categoria', 'titulo']