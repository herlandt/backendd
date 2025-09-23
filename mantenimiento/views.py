from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError
from .models import PersonalMantenimiento, SolicitudMantenimiento
from .serializers import PersonalMantenimientoSerializer, SolicitudMantenimientoSerializer
from usuarios.models import Residente

class PersonalMantenimientoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PersonalMantenimiento.objects.filter(activo=True)
    serializer_class = PersonalMantenimientoSerializer
    permission_classes = [permissions.IsAdminUser]

class SolicitudMantenimientoViewSet(viewsets.ModelViewSet):
    serializer_class = SolicitudMantenimientoSerializer
    permission_classes = [permissions.IsAuthenticated]
    # mantenimiento/views.py

    def get_queryset(self):
        # Si el usuario es superusuario o staff, puede ver todas las solicitudes
        if self.request.user.is_superuser or self.request.user.is_staff:
            return SolicitudMantenimiento.objects.all().order_by('-fecha_creacion')
        
        # Si es un residente normal, solo ve las de su propiedad
        try:
            residente = Residente.objects.get(usuario=self.request.user)
            return SolicitudMantenimiento.objects.filter(propiedad=residente.propiedad).order_by('-fecha_creacion')
        except Residente.DoesNotExist:
            return SolicitudMantenimiento.objects.none() # No devuelve nada si no es residente
    def perform_create(self, serializer):
        try:
            residente = Residente.objects.get(usuario=self.request.user)
            serializer.save(
                solicitado_por=self.request.user,
                propiedad=residente.propiedad
            )
        except Residente.DoesNotExist:
            raise ValidationError("Solo los residentes pueden crear solicitudes.")