# seguridad/views.py
from django.utils import timezone
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Visitante, Visita, Vehiculo
from .serializers import VisitanteSerializer, VisitaSerializer, VehiculoSerializer

# ----- ViewSets CRUD que usas en el router -----

class VisitanteViewSet(viewsets.ModelViewSet):
    queryset = Visitante.objects.all().order_by('nombre_completo')
    serializer_class = VisitanteSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre_completo', 'documento']  # ajusta a tus campos reales
    ordering_fields = ['nombre_completo', 'documento']

class VisitaViewSet(viewsets.ModelViewSet):
    queryset = Visita.objects.select_related('visitante', 'propiedad').all().order_by('-fecha_ingreso_programado')
    serializer_class = VisitaSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['visitante__nombre_completo', 'visitante__documento', 'motivo']
    ordering_fields = ['fecha_ingreso_programado', 'fecha_salida_programada']

class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.select_related('visitante', 'propiedad').all().order_by('placa')
    serializer_class = VehiculoSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    # (A) Búsqueda por placa/marca/modelo
    search_fields = ['placa', 'marca', 'modelo']
    ordering_fields = ['placa', 'marca', 'modelo']

# ----- Tu endpoint de Control de Acceso, sin tocar -----

class ControlAccesoVehicularView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        placa = (request.data.get("placa") or "").strip()
        if not placa:
            return Response({"error": "Se requiere el número de placa."},
                            status=status.HTTP_400_BAD_REQUEST)

        # 1) Vehículo de RESIDENTE (visitante es null)
        v_res = Vehiculo.objects.filter(
            placa__iexact=placa, visitante__isnull=True, propiedad__isnull=False
        ).first()
        if v_res:
            return Response({"status": "Acceso Permitido", "tipo": "Residente"})

        # 2) Vehículo de VISITANTE con visita vigente hoy
        hoy = timezone.localdate()
        visita = (Visita.objects
                  .filter(visitante__vehiculos__placa__iexact=placa,
                          fecha_ingreso_programado__date__lte=hoy,
                          fecha_salida_programada__date__gte=hoy)
                  .select_related("visitante", "propiedad")
                  .first())
        if visita:
            if not visita.ingreso_real:
                visita.ingreso_real = timezone.now()
                visita.save(update_fields=["ingreso_real"])
            return Response({"status": "Acceso Permitido", "tipo": "Visitante",
                             "visita_id": visita.id, "placa": placa})

        return Response({"status": "Acceso Denegado", "placa": placa},
                        status=status.HTTP_403_FORBIDDEN)
# seguridad/views.py
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from .models import Visita

class RegistrarSalidaVehicularView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        placa = (request.data.get("placa") or "").strip()
        if not placa:
            return Response({"error": "Se requiere el número de placa."},
                            status=status.HTTP_400_BAD_REQUEST)

        hoy = timezone.localdate()
        visita = (Visita.objects
                  .filter(visitante__vehiculos__placa__iexact=placa,
                          fecha_ingreso_programado__date__lte=hoy,
                          fecha_salida_programada__date__gte=hoy,
                          ingreso_real__isnull=False,
                          salida_real__isnull=True)   # si tu campo se llama distinto, ajústalo
                  .order_by("-ingreso_real")
                  .first())

        if not visita:
            return Response(
                {"status": "No hay visita activa para registrar salida", "placa": placa},
                status=status.HTTP_404_NOT_FOUND
            )

        visita.salida_real = timezone.now()  # o fecha_salida_real según tu modelo
        visita.save(update_fields=["salida_real"])
        return Response({"status": "Salida Registrada", "visita_id": visita.id, "placa": placa})
