from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import PersonalMantenimiento, SolicitudMantenimiento
from .serializers import (
    PersonalMantenimientoSerializer,
    SolicitudMantenimientoSerializer,
)


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
    permission_classes = [IsStaffOrReadOnly]
    filterset_fields = ["activo", "especialidad"]
    search_fields = ["nombre", "telefono", "especialidad"]
    ordering_fields = ["nombre"]


class SolicitudMantenimientoViewSet(viewsets.ModelViewSet):
    queryset = SolicitudMantenimiento.objects.select_related(
        "propiedad", "asignado_a", "solicitado_por"
    ).all()
    serializer_class = SolicitudMantenimientoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["estado", "propiedad", "asignado_a", "solicitado_por"]
    search_fields = ["titulo", "descripcion", "propiedad__numero_casa", "solicitado_por__username"]
    ordering_fields = ["fecha_creacion", "estado"]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def cambiar_estado(self, request, pk=None):
        """
        Cambia el estado de la solicitud.
        body: {"estado": "ASIGNADO" | "EN_PROCESO" | "RESUELTO" | "CANCELADO"}
        """
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
        """
        Asigna un personal a la solicitud.
        body: {"personal_id": <id|null>}
        """
        solicitud = self.get_object()
        personal_id = request.data.get("personal_id", None)
        if personal_id is None:
            solicitud.asignado_a = None
            # si estaba asignado y lo quitamos, lo pasamos a PENDIENTE
            solicitud.estado = SolicitudMantenimiento.Estados.PENDIENTE
        else:
            try:
                solicitud.asignado_a = PersonalMantenimiento.objects.get(pk=personal_id)
            except PersonalMantenimiento.DoesNotExist:
                return Response({"detail": "personal_id inválido"}, status=status.HTTP_400_BAD_REQUEST)
            # si se asigna, marcamos ASIGNADO si sigue pendiente
            if solicitud.estado == SolicitudMantenimiento.Estados.PENDIENTE:
                solicitud.estado = SolicitudMantenimiento.Estados.ASIGNADO
        solicitud.save(update_fields=["asignado_a", "estado", "fecha_actualizacion"])
        return Response(self.get_serializer(solicitud).data)
