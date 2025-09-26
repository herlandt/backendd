from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Visitante, Visita, Vehiculo
from .serializers import VisitanteSerializer, VisitaSerializer, VehiculoSerializer
from usuarios.models import Residente
from condominio.models import Propiedad


def es_guardia_o_staff(user) -> bool:
    """
    Permite operar como 'guardia' si el usuario:
    - es staff o superuser, o
    - pertenece a un grupo llamado Guardias / Guardia / Seguridad (case-insensitive).
    """
    if user.is_staff or user.is_superuser:
        return True
    return user.groups.filter(name__iexact='Guardias').exists() or \
           user.groups.filter(name__iexact='Guardia').exists() or \
           user.groups.filter(name__iexact='Seguridad').exists()


class VisitanteViewSet(viewsets.ModelViewSet):
    queryset = Visitante.objects.all()
    serializer_class = VisitanteSerializer
    permission_classes = [permissions.IsAuthenticated]


class VisitaViewSet(viewsets.ModelViewSet):
    serializer_class = VisitaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Guardias/Staff ven todo; residentes, solo sus propiedades
        if es_guardia_o_staff(user):
            return Visita.objects.all()
        props = Residente.objects.filter(usuario=user).values_list('propiedad', flat=True)
        return Visita.objects.filter(propiedad__in=list(props))

    def perform_create(self, serializer):
        user = self.request.user

        # Guardias/Staff: pueden indicar cualquier propiedad por ID
        if es_guardia_o_staff(user):
            prop_id = self.request.data.get('propiedad_id')
            if not prop_id:
                raise ValidationError("Para crear como guardia/staff, envía 'propiedad_id'.")
            try:
                propiedad = Propiedad.objects.get(pk=prop_id)
            except Propiedad.DoesNotExist:
                raise ValidationError("La propiedad indicada no existe.")
            serializer.save(registrado_por=user, propiedad=propiedad)
            return

        # Residente: se usa la propiedad asociada al usuario
        try:
            residente = Residente.objects.get(usuario=user)
        except Residente.DoesNotExist:
            raise ValidationError("El usuario no es un residente válido.")
        serializer.save(registrado_por=user, propiedad=residente.propiedad)


class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer
    permission_classes = [permissions.IsAuthenticated]


class ControlAccesoVehicularView(APIView):
    """
    POST { "placa": "ABC123" }
    - Si es de residente -> Acceso Permitido (Residente)
    - Si hay visita programada hoy para un visitante con esa placa -> marca ingreso_real y permite
    - En otro caso -> Acceso Denegado
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        placa = request.data.get('placa')
        if not placa:
            return Response({'error': 'Se requiere el número de placa.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Vehículo de residente (visitante es null)
        vehiculo_residente = Vehiculo.objects.filter(
            placa__iexact=placa, visitante__isnull=True
        ).first()
        if vehiculo_residente:
            return Response({'status': 'Acceso Permitido', 'tipo': 'Residente'})

        # Visita programada hoy
        hoy = timezone.now().date()
        visita_programada = Visita.objects.filter(
            visitante__vehiculos__placa__iexact=placa,
            fecha_ingreso_programado__date=hoy,
        ).first()

        if visita_programada:
            if not visita_programada.ingreso_real:
                visita_programada.ingreso_real = timezone.now()
                visita_programada.save(update_fields=['ingreso_real'])
            return Response({'status': 'Acceso Permitido', 'tipo': 'Visitante'})

        return Response({'status': 'Acceso Denegado', 'placa': placa},
                        status=status.HTTP_403_FORBIDDEN)
