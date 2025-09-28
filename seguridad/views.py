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
from .models import EventoSeguridad, Vehiculo
from .serializers import ConsultaPlacaSerializer, VisitaSerializer
from .permissions import HasAPIKey
# --- Vistas de Control de Acceso ---
from .models import EventoSeguridad 

# seguridad/views.py

# ... (importaciones existentes) ...

class ControlAccesoVehicularView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_scope = "control_acceso"

    def _handle_ingreso(self, placa):
        """ Lógica de negocio para procesar un ingreso. """
        ahora = timezone.now()
        try:
            vehiculo = Vehiculo.objects.get(placa__iexact=placa)
        except Vehiculo.DoesNotExist:
            return Response({"detail": f"Placa '{placa}' no encontrada."}, status=status.HTTP_403_FORBIDDEN)

        # Lógica para residentes (la mantenemos como la tenías)
        if hasattr(vehiculo, 'es_residente') and vehiculo.es_residente:
            # Aquí puedes añadir de nuevo tu lógica de morosidad si la necesitas
            return Response({"detail": "Acceso permitido para residente.", "tipo": "residente"}, status=status.HTTP_200_OK)

        # Lógica para visitantes (la mantenemos como la tenías)
        visita = Visita.objects.filter(
            vehiculo=vehiculo,
            fecha_hora_ingreso__lte=ahora,
            fecha_hora_salida__gte=ahora, # Asumiendo que tu modelo Visita tiene estos campos
            estado='activa'
        ).first()

        if not visita:
            return Response({"detail": "Visitante sin visita programada vigente."}, status=status.HTTP_403_FORBIDDEN)

        visita.fecha_hora_ingreso = ahora # Marcamos el ingreso real
        visita.save()
        return Response({"detail": "Acceso permitido para visitante.", "tipo": "visitante"}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = ConsultaPlacaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        placa = serializer.validated_data["placa"]
        return self._handle_ingreso(placa)


class ControlSalidaVehicularView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_scope = "control_salida"

    def _handle_salida(self, placa):
        """ Lógica de negocio para procesar una salida. """
        try:
            vehiculo = Vehiculo.objects.get(placa__iexact=placa)
        except Vehiculo.DoesNotExist:
            return Response({"detail": "Vehículo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        if hasattr(vehiculo, 'es_residente') and vehiculo.es_residente:
            return Response({"detail": "Salida de residente registrada."}, status=status.HTTP_200_OK)

        visita = Visita.objects.filter(
            vehiculo=vehiculo,
            estado='activa',
            fecha_hora_ingreso__isnull=False
        ).order_by("-fecha_hora_ingreso").first()

        if not visita:
            return Response({"detail": "No se encontró una visita activa para este vehículo."}, status=status.HTTP_404_NOT_FOUND)

        visita.fecha_hora_salida = timezone.now()
        visita.estado = 'finalizada'
        visita.save()
        return Response({"detail": "Salida registrada con éxito."}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = ConsultaPlacaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        placa = serializer.validated_data["placa"]
        return self._handle_salida(placa)

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
    
# seguridad/views.py

# ... (al final del archivo, después de las otras vistas) ...

# ========= VISTA ESPECIAL PARA LA CÁMARA DE IA =========

class IAControlVehicularView(APIView):
    """
    Endpoint para la cámara. Valida la placa, registra el evento y toma una acción.
    """
    permission_classes = [HasAPIKey]

    def _registrar_evento(self, tipo_evento, placa, accion, motivo, vehiculo=None):
        """Función auxiliar para crear el registro del evento."""
        EventoSeguridad.objects.create(
            tipo_evento=tipo_evento,
            placa_detectada=placa,
            accion=accion,
            motivo=motivo,
            vehiculo_registrado=vehiculo
        )

    def post(self, request, *args, **kwargs):
        placa = request.data.get('placa')
        tipo_evento = request.data.get('tipo', 'ingreso').upper() # Convertimos a mayúsculas

        if not placa:
            return Response({"error": "El campo 'placa' es requerido."}, status=status.HTTP_400_BAD_REQUEST)

        # Usamos un bloque try-except para manejar el caso de que el vehículo no exista
        vehiculo = Vehiculo.objects.filter(placa__iexact=placa).first()

        if tipo_evento == 'INGRESO':
            handler_view = ControlAccesoVehicularView()
            response = handler_view._handle_ingreso(placa)
        elif tipo_evento == 'SALIDA':
            handler_view = ControlSalidaVehicularView()
            response = handler_view._handle_salida(placa)
        else:
            return Response({"error": "El campo 'tipo' debe ser 'INGRESO' o 'SALIDA'."}, status=status.HTTP_400_BAD_REQUEST)

        # Después de obtener la respuesta, registramos el evento
        if response.status_code == 200:
            self._registrar_evento(tipo_evento, placa, EventoSeguridad.AccionTomada.PERMITIDO, response.data.get('detail'), vehiculo)
        else:
            self._registrar_evento(tipo_evento, placa, EventoSeguridad.AccionTomada.DENEGADO, response.data.get('detail'), vehiculo)
            
        return response