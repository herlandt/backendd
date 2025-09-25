from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SolicitudMantenimiento
from .serializers import SolicitudMantenimientoSerializer
from .permissions import IsMantenimientoOrAdminUser
from usuarios.models import Residente

class SolicitudMantenimientoViewSet(viewsets.ModelViewSet):
    serializer_class = SolicitudMantenimientoSerializer
    queryset = SolicitudMantenimiento.objects.all()

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'residente'):
            return SolicitudMantenimiento.objects.filter(solicitado_por=user.residente)
        # Usamos la comprobación correcta para el personal de mantenimiento
        elif hasattr(user, 'perfil_mantenimiento') or user.is_staff:
            return SolicitudMantenimiento.objects.all()
        return SolicitudMantenimiento.objects.none()

    def perform_create(self, serializer):
        try:
            residente = Residente.objects.get(usuario=self.request.user)
            serializer.save(solicitado_por=residente)
        except Residente.DoesNotExist:
            raise serializers.ValidationError("El usuario no es un residente válido.")

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'actualizar_estado']:
            permission_classes = [IsMantenimientoOrAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'], url_path='actualizar-estado')
    def actualizar_estado(self, request, pk=None):
        solicitud = self.get_object()
        nuevo_estado = request.data.get('estado')

        # Usamos el nombre correcto de la variable de opciones
        valid_estados = [choice[0] for choice in SolicitudMantenimiento.ESTADO_OPCIONES]
        if nuevo_estado not in valid_estados:
            return Response({'error': f'Estado no válido. Opciones: {valid_estados}'}, status=status.HTTP_400_BAD_REQUEST)

        solicitud.estado = nuevo_estado
        solicitud.save()
        serializer = self.get_serializer(solicitud)
        return Response(serializer.data)