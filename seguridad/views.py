import csv
from datetime import timedelta
from django.db.models import Count
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Vehiculo, Visita
from .serializers import ConsultaPlacaSerializer, VisitaSerializer

# --- Vistas de Control de Acceso ---

class ControlAccesoVehicularView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_scope = "control_acceso"

    def post(self, request, *args, **kwargs):
        serializer = ConsultaPlacaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        placa = serializer.validated_data["placa"]
        ahora = timezone.now()

        try:
            vehiculo = Vehiculo.objects.get(placa__iexact=placa)
        except Vehiculo.DoesNotExist:
            return Response({"detail": "Placa no encontrada."}, status=status.HTTP_403_FORBIDDEN)

        if vehiculo.es_residente:
            return Response({"detail": "Acceso permitido para residente.", "tipo": "residente"}, status=status.HTTP_200_OK)

        visita = Visita.objects.filter(
            visitante__vehiculos=vehiculo,
            fecha_ingreso_programado__lte=ahora,
            fecha_salida_programada__gte=ahora,
            ingreso_real__isnull=True,
        ).first()

        if not visita:
            return Response({"detail": "Visitante sin visita programada vigente."}, status=status.HTTP_403_FORBIDDEN)

        visita.ingreso_real = ahora
        visita.save()
        return Response({"detail": "Acceso permitido para visitante.", "tipo": "visitante"}, status=status.HTTP_200_OK)

class ControlSalidaVehicularView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_scope = "control_salida"

    def post(self, request, *args, **kwargs):
        serializer = ConsultaPlacaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        placa = serializer.validated_data["placa"]
        try:
            vehiculo = Vehiculo.objects.get(placa__iexact=placa)
        except Vehiculo.DoesNotExist:
            return Response({"detail": "Vehículo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        if vehiculo.es_residente:
            return Response({"detail": "Salida de residente registrada."}, status=status.HTTP_200_OK)

        visita = Visita.objects.filter(
            visitante__vehiculos=vehiculo,
            ingreso_real__isnull=False,
            salida_real__isnull=True
        ).order_by("-ingreso_real").first()

        if not visita:
            return Response({"detail": "No se encontró una visita activa para este vehículo."}, status=status.HTTP_404_NOT_FOUND)

        visita.salida_real = timezone.now()
        visita.save()
        return Response({"detail": "Salida registrada con éxito."}, status=status.HTTP_200_OK)

# --- Vistas de Listas y Reportes (Admin) ---

class VisitasAbiertasView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        visitas_abiertas = Visita.objects.filter(ingreso_real__isnull=False, salida_real__isnull=True)
        serializer = VisitaSerializer(visitas_abiertas, many=True)
        return Response(serializer.data)

class ExportVisitasCSVView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="visitas.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Visitante', 'Documento', 'Propiedad', 'Ingreso Real', 'Salida Programada'])
        visitas = Visita.objects.select_related('visitante', 'propiedad').all()
        for v in visitas:
            writer.writerow([v.id, v.visitante.nombre_completo, v.visitante.documento, v.propiedad.numero_casa, v.ingreso_real, v.fecha_salida_programada])
        return response

class CerrarVisitasVencidasView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        from django.core.management import call_command
        call_command('cerrar_visitas_vencidas')
        # La respuesta ahora coincide con lo que el test espera
        return Response({"detail": "Comando para cerrar visitas vencidas ejecutado."}, status=status.HTTP_200_OK)

# --- Vistas de Dashboard (Admin) ---

class DashboardResumenView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        abiertas = Visita.objects.filter(ingreso_real__isnull=False, salida_real__isnull=True).count()
        total_hoy = Visita.objects.filter(ingreso_real__date=timezone.now().date()).count()
        return Response({"visitas_abiertas": abiertas, "total_ingresos_hoy": total_hoy})

class DashboardSeriesView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        # Lógica de ejemplo, puedes mejorarla
        return Response({"series": "data"})

class DashboardTopVisitantesView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        days = int(request.query_params.get('days', 30))
        limit = int(request.query_params.get('limit', 5))
        since = timezone.now() - timedelta(days=days)
        
        top_visitantes = Visita.objects.filter(ingreso_real__gte=since) \
            .values('visitante__nombre_completo') \
            .annotate(count=Count('id')) \
            .order_by('-count')[:limit]
            
        return Response({"items": list(top_visitantes)})