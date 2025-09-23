from rest_framework import viewsets
from .models import Propiedad, AreaComun
from .serializers import PropiedadSerializer, AreaComunSerializer

class PropiedadViewSet(viewsets.ModelViewSet):
    queryset = Propiedad.objects.all().order_by('numero_casa')
    serializer_class = PropiedadSerializer

class AreaComunViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AreaComun.objects.all()
    serializer_class = AreaComunSerializer