from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Propiedad, AreaComun, Aviso, Regla, LecturaAviso
from .serializers import (
    PropiedadSerializer, AreaComunSerializer, AvisoSerializer, 
    ReglaSerializer, LecturaAvisoSerializer, AvisoDetalleSerializer
)

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
    # Filtros avanzados
    filterset_fields = {
        'titulo': ['icontains'],
        'fecha_publicacion': ['gte', 'lte', 'exact'],
        'activo': ['exact'],
        'dirigido_a': ['exact'],
    }
    search_fields = ['titulo', 'contenido']
    ordering_fields = ['fecha_publicacion', 'titulo']
    ordering = ['-fecha_publicacion']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AvisoDetalleSerializer
        return AvisoSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def marcar_como_leido(self, request, pk=None):
        """
        Marca un aviso como leído por el residente autenticado.
        POST /api/condominio/avisos/{id}/marcar_como_leido/
        """
        aviso = self.get_object()
        
        # Verificar que el usuario es un residente
        try:
            from usuarios.models import Residente
            residente = Residente.objects.get(usuario=request.user)
        except Residente.DoesNotExist:
            return Response(
                {'error': 'Solo los residentes pueden marcar avisos como leídos'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar si el aviso está dirigido a este residente
        if aviso.dirigido_a == 'PROPIETARIOS' and residente.rol != 'propietario':
            return Response(
                {'error': 'Este aviso no está dirigido a inquilinos'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        elif aviso.dirigido_a == 'INQUILINOS' and residente.rol != 'inquilino':
            return Response(
                {'error': 'Este aviso no está dirigido a propietarios'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Crear o actualizar la lectura
        lectura, created = LecturaAviso.objects.get_or_create(
            aviso=aviso,
            residente=residente,
            defaults={
                'ip_lectura': self.get_client_ip(request)
            }
        )
        
        if created:
            return Response({
                'message': 'Aviso marcado como leído',
                'fecha_lectura': lectura.fecha_lectura
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Ya habías leído este aviso anteriormente',
                'fecha_lectura': lectura.fecha_lectura
            }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def estadisticas_lectura(self, request, pk=None):
        """
        Obtiene estadísticas detalladas de lectura de un aviso.
        GET /api/condominio/avisos/{id}/estadisticas_lectura/
        """
        aviso = self.get_object()
        
        # Usar el serializer detallado para obtener toda la información
        serializer = AvisoDetalleSerializer(aviso)
        
        return Response({
            'aviso': serializer.data,
            'resumen': {
                'total_residentes_objetivo': aviso.total_residentes_objetivo(),
                'total_lecturas': aviso.total_lecturas(),
                'porcentaje_lectura': aviso.porcentaje_lectura(),
                'pendientes_por_leer': aviso.total_residentes_objetivo() - aviso.total_lecturas()
            }
        })

    @action(detail=False, methods=['get'])
    def mis_avisos_pendientes(self, request):
        """
        Obtiene los avisos que el residente autenticado no ha leído.
        GET /api/condominio/avisos/mis_avisos_pendientes/
        """
        # Verificar que el usuario es un residente
        try:
            from usuarios.models import Residente
            residente = Residente.objects.get(usuario=request.user)
        except Residente.DoesNotExist:
            return Response(
                {'error': 'Solo los residentes pueden consultar avisos pendientes'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Filtrar avisos según el rol del residente
        avisos_query = Aviso.objects.filter(activo=True)
        
        if residente.rol == 'propietario':
            avisos_query = avisos_query.filter(dirigido_a__in=['TODOS', 'PROPIETARIOS'])
        elif residente.rol == 'inquilino':
            avisos_query = avisos_query.filter(dirigido_a__in=['TODOS', 'INQUILINOS'])
        
        # Excluir avisos ya leídos
        avisos_leidos = LecturaAviso.objects.filter(residente=residente).values_list('aviso_id', flat=True)
        avisos_pendientes = avisos_query.exclude(id__in=avisos_leidos)
        
        serializer = AvisoSerializer(avisos_pendientes, many=True)
        
        return Response({
            'avisos_pendientes': serializer.data,
            'total_pendientes': avisos_pendientes.count()
        })

    def get_client_ip(self, request):
        """Obtiene la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class LecturaAvisoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar las lecturas de avisos.
    Solo lectura - las lecturas se crean a través del endpoint marcar_como_leido
    """
    queryset = LecturaAviso.objects.all()
    serializer_class = LecturaAvisoSerializer
    
    # Filtros avanzados
    filterset_fields = {
        'aviso': ['exact'],
        'residente': ['exact'],
        'fecha_lectura': ['gte', 'lte', 'exact'],
    }
    search_fields = [
        'residente__usuario__username', 
        'residente__usuario__email',
        'aviso__titulo'
    ]
    ordering_fields = ['fecha_lectura']
    ordering = ['-fecha_lectura']

    @action(detail=False, methods=['get'])
    def por_aviso(self, request):
        """
        Filtra lecturas por aviso específico.
        GET /api/condominio/lecturas-avisos/por_aviso/?aviso_id=1
        """
        aviso_id = request.query_params.get('aviso_id')
        if not aviso_id:
            return Response(
                {'error': 'Parámetro aviso_id es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lecturas = self.queryset.filter(aviso_id=aviso_id)
        serializer = self.get_serializer(lecturas, many=True)
        
        return Response({
            'lecturas': serializer.data,
            'total': lecturas.count()
        })

    @action(detail=False, methods=['get'])
    def resumen_general(self, request):
        """
        Resumen general de lecturas de todos los avisos activos.
        GET /api/condominio/lecturas-avisos/resumen_general/
        """
        from django.db.models import Count
        
        avisos_con_stats = Aviso.objects.filter(activo=True).annotate(
            total_lecturas=Count('lecturas')
        ).order_by('-fecha_publicacion')
        
        resumen = []
        for aviso in avisos_con_stats:
            resumen.append({
                'aviso_id': aviso.id,
                'titulo': aviso.titulo,
                'dirigido_a': aviso.dirigido_a,
                'fecha_publicacion': aviso.fecha_publicacion,
                'total_residentes_objetivo': aviso.total_residentes_objetivo(),
                'total_lecturas': aviso.total_lecturas(),
                'porcentaje_lectura': aviso.porcentaje_lectura(),
                'pendientes': aviso.total_residentes_objetivo() - aviso.total_lecturas()
            })
        
        return Response({
            'avisos': resumen,
            'total_avisos_activos': len(resumen)
        })

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