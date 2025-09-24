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