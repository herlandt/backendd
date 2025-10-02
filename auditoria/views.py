# auditoria/views.py
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters
from .models import Bitacora
from .serializers import BitacoraSerializer

class BitacoraFilter(django_filters.FilterSet):
    """Filtros para la bitácora de auditoría"""
    timestamp__gte = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    timestamp__lte = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    accion__icontains = django_filters.CharFilter(field_name='accion', lookup_expr='icontains')
    usuario = django_filters.NumberFilter(field_name='usuario__id')
    ip_address = django_filters.CharFilter(field_name='ip_address')
    
    class Meta:
        model = Bitacora
        fields = ['usuario', 'accion__icontains', 'timestamp__gte', 'timestamp__lte', 'ip_address']

class BitacoraViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para consultar la bitácora de auditoría.
    Solo administradores pueden acceder.
    """
    queryset = Bitacora.objects.all()
    serializer_class = BitacoraSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BitacoraFilter
    search_fields = ['accion', 'descripcion', 'usuario__username']
    ordering_fields = ['timestamp', 'usuario', 'accion']
    ordering = ['-timestamp']  # Más recientes primero