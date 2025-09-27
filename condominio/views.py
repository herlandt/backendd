from rest_framework import viewsets
from .models import Propiedad, AreaComun, Aviso
from .serializers import PropiedadSerializer, AreaComunSerializer, AvisoSerializer

class PropiedadViewSet(viewsets.ModelViewSet):
    queryset = Propiedad.objects.all().order_by('numero_casa')
    serializer_class = PropiedadSerializer

class AreaComunViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AreaComun.objects.all()
    serializer_class = AreaComunSerializer


# --- AÑADE ESTA CLASE ---
class AvisoViewSet(viewsets.ModelViewSet):
    queryset = Aviso.objects.all()
    serializer_class = AvisoSerializer

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
    serializer_class = ReglaSerializer
    permission_classes = [permissions.IsAuthenticated] # Solo usuarios autenticados pueden ver las reglas