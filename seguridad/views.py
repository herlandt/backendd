# seguridad/views.py
from datetime import date, datetime, time, timedelta
import csv
import io

from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.db.models import Count
from django.db.models.functions import TruncDate

from rest_framework import status, viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Vehiculo, Visita, Visitante
from .serializers import VehiculoSerializer, VisitaSerializer, VisitanteSerializer

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from drf_spectacular.utils import (
    extend_schema, OpenApiResponse, OpenApiParameter, OpenApiTypes, inline_serializer
)
from rest_framework import serializers
from drf_spectacular.utils import (
    extend_schema, OpenApiResponse, OpenApiParameter, OpenApiTypes, inline_serializer
)

# --- ViewSets CRUD ---
# Heredan IsAuthenticated por DEFAULT_PERMISSION_CLASSES en settings
class VisitanteViewSet(viewsets.ModelViewSet):
    queryset = Visitante.objects.all().order_by("nombre_completo")
    serializer_class = VisitanteSerializer


class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.select_related("propiedad", "visitante").all().order_by("placa")
    serializer_class = VehiculoSerializer


class VisitaViewSet(viewsets.ModelViewSet):
    queryset = Visita.objects.select_related("visitante", "propiedad").all().order_by("-fecha_ingreso_programado")
    serializer_class = VisitaSerializer
class _PlacaInSerializer(serializers.Serializer):
    placa = serializers.CharField()

@extend_schema(
    summary="Control de acceso vehicular",
    request=_PlacaInSerializer,
    responses={
        200: OpenApiResponse(
            inline_serializer("AccesoOK", {
                "permitido": serializers.BooleanField(),
                "tipo": serializers.CharField(),
                "placa": serializers.CharField(),
                "visita_id": serializers.IntegerField(required=False),
            })
        ),
        403: OpenApiResponse(
            inline_serializer("AccesoDenied", {
                "permitido": serializers.BooleanField(),
                "status": serializers.CharField(required=False),
                "motivo": serializers.CharField(),
                "tipo": serializers.CharField(required=False),
                "placa": serializers.CharField(required=False),
            })
        ),
    },
)


# --- Control de ACCESO vehicular ---
class ControlAccesoVehicular(APIView):
    """
    POST { "placa": "ABC123" }
    - Residente: permitido True, tipo "Residente"
    - Visitante con visita vigente: permitido True, tipo "Visitante" y marca ingreso_real si no existe
    - Desconocido: 403, status "Acceso Denegado"
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_scope = "control_acceso"

    def post(self, request):
        placa = (request.data.get("placa") or "").strip().upper()
        if not placa:
            return Response({"detail": "placa requerida"}, status=status.HTTP_400_BAD_REQUEST)

        veh = Vehiculo.objects.select_related("propiedad", "visitante").filter(placa=placa).first()
        if not veh:
            return Response(
                {"permitido": False, "status": "Acceso Denegado", "motivo": "Placa no registrada"},
                status=status.HTTP_403_FORBIDDEN,
            )

        now = timezone.now()

        # Residente
        if veh.propiedad_id and not veh.visitante_id:
            return Response({"permitido": True, "tipo": "Residente", "placa": placa}, status=status.HTTP_200_OK)

        # Visitante
        if veh.visitante_id:
            visita = (
                Visita.objects.filter(
                    visitante=veh.visitante,
                    fecha_ingreso_programado__lte=now,
                    fecha_salida_programada__gte=now,
                )
                .order_by("-fecha_ingreso_programado")
                .first()
            )
            if not visita:
                return Response(
                    {
                        "permitido": False,
                        "status": "Acceso Denegado",
                        "tipo": "Visitante",
                        "placa": placa,
                        "motivo": "No tiene visita programada vigente",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            if visita.ingreso_real is None:
                visita.ingreso_real = now
                visita.save(update_fields=["ingreso_real"])

            return Response(
                {"permitido": True, "tipo": "Visitante", "placa": placa, "visita_id": visita.id},
                status=status.HTTP_200_OK,
            )

        # Estado inválido
        return Response(
            {"permitido": False, "status": "Acceso Denegado", "motivo": "Configuración del vehículo inválida"},
            status=status.HTTP_403_FORBIDDEN,
        )

@extend_schema(
    summary="Control de salida vehicular",
    request=_PlacaInSerializer,
    responses={
        200: OpenApiResponse(
            inline_serializer("SalidaOK", {
                "permitido": serializers.BooleanField(),
                "tipo": serializers.CharField(),
                "placa": serializers.CharField(),
                "visita_id": serializers.IntegerField(required=False),
                "motivo": serializers.CharField(required=False),
            })
        ),
        403: OpenApiResponse(
            inline_serializer("SalidaDenied", {
                "permitido": serializers.BooleanField(),
                "motivo": serializers.CharField(),
            })
        ),
    },
)

# --- Control de SALIDA vehicular ---
class ControlSalidaVehicular(APIView):
    """
    POST { "placa": "XYZ123" }
    - Residente: permitido True, tipo = "residente" (minúscula).
    - Visitante sin ingreso: 200 con permitido False y motivo "No hay registro de ingreso".
    - Visitante con ingreso: cierra la visita (salida_real=now).
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_scope = "control_salida"
    def post(self, request):
        placa = (request.data.get("placa") or "").strip().upper()
        if not placa:
            return Response({"detail": "Falta 'placa'."}, status=status.HTTP_400_BAD_REQUEST)

        veh = Vehiculo.objects.filter(placa=placa).select_related("visitante", "propiedad").first()
        if not veh:
            return Response({"permitido": False, "motivo": "Placa no registrada"}, status=status.HTTP_403_FORBIDDEN)

        # Residente => propiedad no nula
        if veh.propiedad_id:
            return Response({"permitido": True, "tipo": "residente", "placa": placa}, status=status.HTTP_200_OK)

        # Visitante
        if veh.visitante_id is None:
            return Response(
                {"permitido": False, "tipo": "Visitante", "placa": placa, "motivo": "Placa de visitante sin persona asociada"},
                status=status.HTTP_403_FORBIDDEN,
            )

        now = timezone.now()
        visita = (
            Visita.objects.filter(visitante=veh.visitante, ingreso_real__isnull=False, salida_real__isnull=True)
            .order_by("-ingreso_real", "-fecha_ingreso_programado")
            .first()
        )

        if not visita:
            return Response(
                {"permitido": False, "tipo": "Visitante", "placa": placa, "motivo": "No hay registro de ingreso"},
                status=status.HTTP_200_OK,
            )

        if visita.salida_real is None:
            visita.salida_real = now
            visita.save(update_fields=["salida_real"])

        return Response({"permitido": True, "tipo": "Visitante", "placa": placa, "visita_id": visita.id}, status=status.HTTP_200_OK)

@extend_schema(
    summary="Lista de visitas abiertas (sin salida_real)",
    responses=OpenApiResponse(
        inline_serializer("VisitaAbierta", {
            "id": serializers.IntegerField(),
            "visitante": serializers.CharField(allow_null=True),
            "documento": serializers.CharField(allow_null=True),
            "propiedad": serializers.CharField(allow_null=True),
            "ingreso_real": serializers.DateTimeField(allow_null=True),
            "salida_programada": serializers.DateTimeField(allow_null=True),
        }), many=True
    ),
)

# --- Listado de visitas abiertas ---
class VisitasAbiertasView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        abiertas = Visita.objects.select_related("visitante", "propiedad").filter(
            ingreso_real__isnull=False, salida_real__isnull=True
        )
        data = [
            {
                "id": v.id,
                "visitante": v.visitante.nombre_completo if v.visitante_id else None,
                "documento": v.visitante.documento if v.visitante_id else None,
                "propiedad": str(v.propiedad) if v.propiedad_id else None,
                "ingreso_real": v.ingreso_real,
                "salida_programada": v.fecha_salida_programada,
            }
            for v in abiertas
        ]
        return Response(data, status=status.HTTP_200_OK)

@extend_schema(
    summary="Cierra visitas vencidas (POST)",
    responses=OpenApiResponse(
        inline_serializer("CerrarVencidasResp", {"cerradas": serializers.IntegerField()})
    ),
)

# --- Cerrar visitas vencidas (endpoint) ---
class CerrarVisitasVencidas(APIView):
    """
    POST sin body. Cierra (pone salida_real=fecha_salida_programada) las visitas:
      - ingreso_real != null
      - salida_real == null
      - fecha_salida_programada < ahora
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        now = timezone.now()
        qs = Visita.objects.filter(ingreso_real__isnull=False, salida_real__isnull=True, fecha_salida_programada__lt=now)
        cerradas = 0
        for v in qs:
            v.salida_real = v.fecha_salida_programada
            v.save(update_fields=["salida_real"])
            cerradas += 1
        return Response({"cerradas": cerradas}, status=status.HTTP_200_OK)

@extend_schema(
    summary="Dashboard/resumen",
    parameters=[
        OpenApiParameter("fecha", OpenApiTypes.DATE, description="YYYY-MM-DD", required=False),
        OpenApiParameter("propiedad", OpenApiTypes.INT, required=False),
        OpenApiParameter("days", OpenApiTypes.INT, required=False),
    ],
    responses=OpenApiResponse(
        inline_serializer("DashResumen", {
            "fecha": serializers.DateField(),
            "programadas": serializers.IntegerField(),
            "ingresos": serializers.IntegerField(),
            "salidas": serializers.IntegerField(),
            "abiertas": serializers.IntegerField(),
            "vencidas_abiertas": serializers.IntegerField(),
            "visitantes_unicos": serializers.IntegerField(),
        })
    ),
)

# --- Dashboard: resumen ---
class DashboardResumenView(APIView):
    """
    GET /api/seguridad/dashboard/resumen/?fecha=YYYY-MM-DD&propiedad=<id>&days=30
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            target = date.fromisoformat(request.query_params.get("fecha") or timezone.localdate().isoformat())
        except ValueError:
            return Response({"detail": "fecha inválida. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        prop_id = request.query_params.get("propiedad")
        try:
            days = int(request.query_params.get("days", 30))
        except ValueError:
            days = 30

        qs = Visita.objects.all()
        if prop_id:
            qs = qs.filter(propiedad_id=prop_id)

        start_dt = timezone.make_aware(datetime.combine(target, datetime.min.time()))
        end_dt = timezone.make_aware(datetime.combine(target, datetime.max.time()))

        programadas = qs.filter(fecha_ingreso_programado__range=(start_dt, end_dt)).count()
        ingresos = qs.filter(ingreso_real__range=(start_dt, end_dt)).count()
        salidas = qs.filter(salida_real__range=(start_dt, end_dt)).count()

        ahora = timezone.now()
        abiertas = qs.filter(ingreso_real__isnull=False, salida_real__isnull=True).count()
        vencidas_abiertas = qs.filter(salida_real__isnull=True, fecha_salida_programada__lt=ahora).count()

        desde = ahora - timedelta(days=days)
        visitantes_unicos = qs.filter(fecha_ingreso_programado__gte=desde).values("visitante_id").distinct().count()

        data = {
            "fecha": target.isoformat(),
            "programadas": programadas,
            "ingresos": ingresos,
            "salidas": salidas,
            "abiertas": abiertas,
            "vencidas_abiertas": vencidas_abiertas,
            "visitantes_unicos": visitantes_unicos,
        }
        return Response(data, status=status.HTTP_200_OK)

@extend_schema(
    summary="Dashboard/series",
    parameters=[
        OpenApiParameter("from", OpenApiTypes.DATE, required=False),
        OpenApiParameter("to", OpenApiTypes.DATE, required=False),
        OpenApiParameter("propiedad", OpenApiTypes.INT, required=False),
    ],
    responses=OpenApiResponse(
        inline_serializer("DashSeriesResp", {
            "from": serializers.DateField(),
            "to": serializers.DateField(),
            "items": serializers.ListSerializer(
                child=inline_serializer("DashPoint", {
                    "date": serializers.DateField(),
                    "programadas": serializers.IntegerField(),
                    "ingresos": serializers.IntegerField(),
                    "salidas": serializers.IntegerField(),
                })
            ),
        })
    ),
)

# --- Dashboard: series ---
class DashboardSeriesView(APIView):
    """
    GET /api/seguridad/dashboard/series/?from=YYYY-MM-DD&to=YYYY-MM-DD&propiedad=<id>
    Respuesta:
    {
      "from": "YYYY-MM-DD",
      "to": "YYYY-MM-DD",
      "items": [
        { "date": "YYYY-MM-DD", "programadas": N, "ingresos": N, "salidas": N }, ...
      ]
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        try:
            start = date.fromisoformat(request.query_params["from"]) if request.query_params.get("from") else today - timedelta(days=6)
            end = date.fromisoformat(request.query_params["to"]) if request.query_params.get("to") else today
        except ValueError:
            return Response({"detail": "Parámetros from/to inválidos. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        if start > end:
            start, end = end, start

        prop_id = request.query_params.get("propiedad")
        qs = Visita.objects.all()
        if prop_id:
            qs = qs.filter(propiedad_id=prop_id)

        items = []
        cur = start
        while cur <= end:
            s = timezone.make_aware(datetime.combine(cur, datetime.min.time()))
            e = timezone.make_aware(datetime.combine(cur, datetime.max.time()))
            items.append(
                {
                    "date": cur.isoformat(),
                    "programadas": qs.filter(fecha_ingreso_programado__range=(s, e)).count(),
                    "ingresos": qs.filter(ingreso_real__range=(s, e)).count(),
                    "salidas": qs.filter(salida_real__range=(s, e)).count(),
                }
            )
            cur += timedelta(days=1)

        return Response({"from": start.isoformat(), "to": end.isoformat(), "items": items}, status=status.HTTP_200_OK)

@extend_schema(
    summary="Top visitantes",
    parameters=[
        OpenApiParameter("days", OpenApiTypes.INT, required=False),
        OpenApiParameter("limit", OpenApiTypes.INT, required=False),
    ],
    responses=OpenApiResponse(
        inline_serializer("TopVisitantesResp", {
            "days": serializers.IntegerField(),
            "items": serializers.ListSerializer(
                child=inline_serializer("TopVisit", {
                    "visitante_id": serializers.IntegerField(),
                    "nombre": serializers.CharField(),
                    "documento": serializers.CharField(allow_null=True),
                    "visitas": serializers.IntegerField(),
                })
            ),
        })
    ),
)

# --- Dashboard: top visitantes ---
class DashboardTopVisitantes(APIView):
    """
    GET /api/seguridad/dashboard/top-visitantes/?days=30&limit=5
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            days = int(request.query_params.get("days", 30))
        except ValueError:
            days = 30
        try:
            limit = int(request.query_params.get("limit", 5))
        except ValueError:
            limit = 5

        start = (timezone.now() - timezone.timedelta(days=days)).date()
        qs = (
            Visita.objects.filter(fecha_ingreso_programado__date__gte=start)
            .values("visitante__id", "visitante__nombre_completo", "visitante__documento")
            .annotate(total=Count("id"))
            .order_by("-total")[:limit]
        )

        data = [
            {
                "visitante_id": x["visitante__id"],
                "nombre": x["visitante__nombre_completo"],
                "documento": x["visitante__documento"],
                "visitas": x["total"],
            }
            for x in qs
        ]
        return Response({"days": days, "items": data}, status=status.HTTP_200_OK)

@extend_schema(
    summary="Exportar visitas en CSV",
    parameters=[
        OpenApiParameter("from", OpenApiTypes.DATETIME, required=False),
        OpenApiParameter("to", OpenApiTypes.DATETIME, required=False),
        OpenApiParameter("desde", OpenApiTypes.DATETIME, required=False),
        OpenApiParameter("hasta", OpenApiTypes.DATETIME, required=False),
    ],
    responses={200: OpenApiResponse(response=OpenApiTypes.BINARY, media_type="text/csv")},
)

# --- Export CSV ---
class ExportVisitasCSV(APIView):
    # Solo admin puede exportar
    permission_classes = [permissions.IsAdminUser]

    def _parse_dt(self, raw, end_of_day=False):
        """Acepta 'YYYY-MM-DD' o 'YYYY-MM-DDTHH:MM[:SS]'. Devuelve datetime aware."""
        if not raw:
            return None
        tz = timezone.get_current_timezone()
        try:
            if "T" in raw:
                dt = datetime.fromisoformat(raw)
            else:
                if end_of_day:
                    dt = datetime.combine(datetime.fromisoformat(raw).date(), time(23, 59, 59))
                else:
                    dt = datetime.combine(datetime.fromisoformat(raw).date(), time(0, 0, 0))
        except ValueError:
            return None
        return timezone.make_aware(dt, tz) if timezone.is_naive(dt) else dt.astimezone(tz)

    def get(self, request):
        raw_from = request.GET.get("from") or request.GET.get("desde")
        raw_to = request.GET.get("to") or request.GET.get("hasta")

        dt_from = self._parse_dt(raw_from, end_of_day=False)
        dt_to = self._parse_dt(raw_to, end_of_day=True)

        qs = Visita.objects.select_related("visitante", "propiedad").all()
        if dt_from:
            qs = qs.filter(fecha_ingreso_programado__gte=dt_from)
        if dt_to:
            qs = qs.filter(fecha_salida_programada__lte=dt_to)

        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(
            [
                "id",
                "visitante_documento",
                "visitante_nombre",
                "propiedad",
                "ingreso_real",
                "salida_real",
                "ingreso_programado",
                "salida_programada",
                "estado",
            ]
        )

        now = timezone.now()
        for v in qs.order_by("id"):
            estado = "Abierta" if v.ingreso_real and not v.salida_real and v.fecha_salida_programada >= now else "Cerrada"
            writer.writerow(
                [
                    v.id,
                    getattr(v.visitante, "documento", "") or "",
                    getattr(v.visitante, "nombre_completo", "") or "",
                    getattr(v.propiedad, "numero_casa", "") or "",
                    v.ingreso_real.isoformat() if v.ingreso_real else "",
                    v.salida_real.isoformat() if v.salida_real else "",
                    v.fecha_ingreso_programado.isoformat() if v.fecha_ingreso_programado else "",
                    v.fecha_salida_programada.isoformat() if v.fecha_salida_programada else "",
                    estado,
                ]
            )

        resp = HttpResponse(buf.getvalue(), content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = 'attachment; filename="visitas.csv"'
        return resp
