from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from .models import Visitante, Visita, Vehiculo
from .serializers import VisitanteSerializer, VisitaSerializer, VehiculoSerializer
from usuarios.models import Residente

class VisitanteViewSet(viewsets.ModelViewSet):
    queryset = Visitante.objects.all()
    serializer_class = VisitanteSerializer
    permission_classes = [permissions.IsAuthenticated]

class VisitaViewSet(viewsets.ModelViewSet):
    serializer_class = VisitaSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        propiedades_usuario = Residente.objects.filter(usuario=self.request.user).values_list('propiedad', flat=True)
        return Visita.objects.filter(propiedad__in=propiedades_usuario)

    def perform_create(self, serializer):
        try:
            residente = Residente.objects.get(usuario=self.request.user)
            serializer.save(registrado_por=self.request.user, propiedad=residente.propiedad)
        except Residente.DoesNotExist:
            raise ValidationError("El usuario no es un residente válido.")

class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer

class ControlAccesoVehicularView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        placa = request.data.get('placa')
        if not placa:
            return Response({'error': 'Se requiere el número de placa.'}, status=status.HTTP_400_BAD_REQUEST)

        vehiculo_residente = Vehiculo.objects.filter(placa__iexact=placa, visitante__isnull=True).first()
        if vehiculo_residente:
            return Response({'status': 'Acceso Permitido', 'tipo': 'Residente'})

        hoy = timezone.now().date()
        visita_programada = Visita.objects.filter(
            visitante__vehiculos__placa__iexact=placa,
            fecha_ingreso_programado__date=hoy
        ).first()
        if visita_programada:
            visita_programada.ingreso_real = timezone.now()
            visita_programada.save()
            return Response({'status': 'Acceso Permitido', 'tipo': 'Visitante'})

        return Response({'status': 'Acceso Denegado', 'placa': placa}, status=status.HTTP_403_FORBIDDEN)