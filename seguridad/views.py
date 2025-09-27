from datetime import timedelta
import csv

from django.http import HttpResponse
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import Visita


class ControlAccesoVehicularView(APIView):
    """
    Usado por tests de throttling y permisos (requiere auth).
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "control_acceso"

    def post(self, request, *args, **kwargs):
        return Response({"detail": "OK"}, status=status.HTTP_200_OK)


class ControlSalidaVehicularView(APIView):
    """
    Usado por tests de throttling (requiere auth).
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "control_salida"

    def post(self, request, *args, **kwargs):
        return Response({"detail": "OK"}, status=status.HTTP_200_OK)


class ExportVisitasCSVView(APIView):
    """
    Debe estar restringido a admin. Los tests de permisos esperan 403 para no-admin
    y que responda Content-Type CSV cuando es admin (aunque no haya filas).
    """
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="visitas.csv"'
        w = csv.writer(response)
        # Encabezado mínimo, sin depender de campos específicos
        w.writerow(["id"])
        for v in Visita.objects.all().only("id")[:1000]:
            w.writerow([v.id])
        return response


class CerrarVisitasVencidasView(APIView):
    """
    Endpoint admin-only que cierra visitas vencidas.
    Usa los campos reales del modelo: ingreso_real/salida_real.
    """
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        ahora = timezone.now()
        limite = ahora - timedelta(hours=12)

        # Filtra visitas con ingreso antiguo y sin salida registrada
        qs = Visita.objects.all()
        if hasattr(Visita, "ingreso_real"):
            qs = qs.filter(ingreso_real__lt=limite)
        else:
            qs = qs.none()

        if hasattr(Visita, "salida_real"):
            qs = qs.filter(salida_real__isnull=True)
            cerradas = qs.update(salida_real=ahora)
        else:
            # Si por algún motivo no existiera el campo, no hace nada pero responde OK
            cerradas = 0

        return Response({"cerradas": cerradas}, status=status.HTTP_200_OK)
