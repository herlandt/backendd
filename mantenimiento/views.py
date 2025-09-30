from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from finanzas.services import es_residente_moroso 
from .models import PersonalMantenimiento, SolicitudMantenimiento
from .serializers import (
    PersonalMantenimientoSerializer,
    SolicitudMantenimientoSerializer,
)
from usuarios.permissions import IsPropietario, IsPersonalMantenimiento


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Lectura para todos los autenticados; escritura solo staff.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class PersonalMantenimientoViewSet(viewsets.ModelViewSet):
    queryset = PersonalMantenimiento.objects.all()
    serializer_class = PersonalMantenimientoSerializer
    # Filtros avanzados
    filterset_fields = {
        'activo': ['exact'],
        'especialidad': ['exact', 'icontains'],
        'nombre': ['icontains'],
    }
    search_fields = ['nombre', 'telefono', 'especialidad']
    ordering_fields = ['nombre', 'especialidad']
    ordering = ['nombre']

    def get_permissions(self):
        # Solo propietarios pueden gestionar personal de mantenimiento
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsPropietario]
        # Cualquier usuario autenticado puede ver personal de mantenimiento
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

class SolicitudMantenimientoViewSet(viewsets.ModelViewSet):
    serializer_class = SolicitudMantenimientoSerializer
    # Filtros avanzados
    filterset_fields = {
        'estado': ['exact'],
        'propiedad': ['exact'],
        'asignado_a': ['exact'],
        'solicitado_por': ['exact'],
        'fecha_creacion': ['gte', 'lte', 'exact'],
        'fecha_resolucion': ['gte', 'lte', 'exact', 'isnull'],
        'prioridad': ['exact'],
    }
    search_fields = ['titulo', 'descripcion', 'propiedad__numero', 'solicitado_por__username']
    ordering_fields = ['fecha_creacion', 'estado', 'prioridad']
    ordering = ['-fecha_creacion']

    def get_queryset(self):
        """
        Filtra las solicitudes según el rol del usuario:
        - PROPIETARIO: Ve todas las solicitudes del condominio
        - MANTENIMIENTO: Ve solicitudes asignadas a él
        - RESIDENTE: Ve solo solicitudes que él creó
        """
        user = self.request.user
        
        try:
            if user.profile.role == 'PROPIETARIO':
                # El propietario ve todas las solicitudes
                return SolicitudMantenimiento.objects.select_related(
                    "propiedad", "asignado_a", "solicitado_por"
                ).all()
            elif user.profile.role == 'MANTENIMIENTO':
                # Personal de mantenimiento ve solicitudes asignadas a él
                return SolicitudMantenimiento.objects.select_related(
                    "propiedad", "asignado_a", "solicitado_por"
                ).filter(asignado_a=user)
            else:
                # Residentes ven solo las solicitudes que crearon
                return SolicitudMantenimiento.objects.select_related(
                    "propiedad", "asignado_a", "solicitado_por"
                ).filter(solicitado_por=user)
        except:
            return SolicitudMantenimiento.objects.none()

    def get_permissions(self):
        # Personal de mantenimiento puede gestionar solicitudes asignadas
        # Propietarios pueden gestionar todas las solicitudes
        if self.action in ['update', 'partial_update']:
            self.permission_classes = [IsPersonalMantenimiento]
        elif self.action in ['create', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated]  # Cualquiera puede crear solicitudes
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    # --- MÉTODO AÑADIDO PARA VALIDACIÓN ---
    def perform_create(self, serializer):
        """
        Este método se llama justo antes de guardar una nueva solicitud.
        Aquí añadimos la validación de deudas.
        """
        # Verificamos si el usuario que está creando la solicitud es moroso
        if es_residente_moroso(self.request.user):
            # Si es moroso, lanzamos un error y no permitimos la creación.
            raise serializers.ValidationError("No se pueden crear solicitudes de mantenimiento con deudas pendientes.")
        
        # Si no es moroso, procedemos a guardar la solicitud asociándola al usuario actual.
        serializer.save(solicitado_por=self.request.user)


    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def cambiar_estado(self, request, pk=None):
        # ... (tu código existente aquí, no necesita cambios)
        solicitud = self.get_object()
        nuevo = request.data.get("estado")
        validos = [choice for (choice, _) in SolicitudMantenimiento.Estados.choices]
        if nuevo not in validos:
            return Response(
                {"detail": f"Estado inválido. Válidos: {validos}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        solicitud.estado = nuevo
        solicitud.save(update_fields=["estado", "fecha_actualizacion"])
        return Response(self.get_serializer(solicitud).data)


    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def asignar(self, request, pk=None):
        # ... (tu código existente aquí, no necesita cambios)
        solicitud = self.get_object()
        personal_id = request.data.get("personal_id", None)
        if personal_id is None:
            solicitud.asignado_a = None
            solicitud.estado = SolicitudMantenimiento.Estados.PENDIENTE
        else:
            try:
                solicitud.asignado_a = PersonalMantenimiento.objects.get(pk=personal_id)
            except PersonalMantenimiento.DoesNotExist:
                return Response({"detail": "personal_id inválido"}, status=status.HTTP_400_BAD_REQUEST)
            if solicitud.estado == SolicitudMantenimiento.Estados.PENDIENTE:
                solicitud.estado = SolicitudMantenimiento.Estados.ASIGNADO
        solicitud.save(update_fields=["asignado_a", "estado", "fecha_actualizacion"])
        return Response(self.get_serializer(solicitud).data)
