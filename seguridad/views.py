from datetime import timedelta

from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Visitante, Vehiculo, Visita
from .serializers import VisitanteSerializer, VehiculoSerializer, VisitaSerializer


# --- CRUDs ---
class VisitanteViewSet(viewsets.ModelViewSet):
    queryset = Visitante.objects.all()
    serializer_class = VisitanteSerializer


class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.select_related("propiedad", "visitante").all()
    serializer_class = VehiculoSerializer


class VisitaViewSet(viewsets.ModelViewSet):
    queryset = Visita.objects.select_related("visitante", "propiedad").all()
    serializer_class = VisitaSerializer


# -------- CONTROL DE ACCESO --------
@api_view(["POST"])
def control_acceso_vehicular(request):
    """
    Entrada al condominio por placa.
    - Residente: permitido.
    - Visitante: necesita visita vigente; marca ingreso_real si no estaba.
    - Desconocido: 403 + status "Acceso Denegado".
    Body: {"placa": "..."}
    """
    placa = str(request.data.get("placa", "")).strip().upper()
    if not placa:
        return Response({"detail": "Debe enviar 'placa'."}, status=status.HTTP_400_BAD_REQUEST)

    vehiculo = (
        Vehiculo.objects.filter(placa=placa)
        .select_related("propiedad", "visitante")
        .first()
    )
    if not vehiculo:
        return Response(
            {"permitido": False, "status": "Acceso Denegado", "motivo": "Placa no registrada"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Residente
    if vehiculo.propiedad_id:
        return Response(
            {
                "permitido": True,
                "tipo": "Residente",
                "placa": placa,
                "propiedad": vehiculo.propiedad.numero_casa if vehiculo.propiedad else None,
                "mensaje": "Acceso permitido a residente",
            }
        )

    # Visitante
    if vehiculo.visitante_id:
        now = timezone.now()
        visita = (
            Visita.objects.filter(
                visitante=vehiculo.visitante,
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
                    "motivo": "No existe visita vigente",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if visita.ingreso_real is None:
            visita.ingreso_real = now
            visita.save(update_fields=["ingreso_real"])

        return Response(
            {
                "permitido": True,
                "tipo": "Visitante",
                "placa": placa,
                "visita_id": visita.id,
                "mensaje": "Acceso permitido a visitante",
            }
        )

    # Vehículo sin relación válida
    return Response(
        {"permitido": False, "status": "Acceso Denegado", "motivo": "Vehículo sin asociación válida"},
        status=status.HTTP_403_FORBIDDEN,
    )


# -------- CONTROL DE SALIDA --------
@api_view(["POST"])
def control_salida_vehicular(request):
    """
    Salida por placa.
    - Residente: permitido (idempotente). tipo = "residente" (minúsculas).
    - Visitante: solo si hay visita vigente con ingreso_real; al salir, marca salida_real.
      Si no hubo ingreso, deniega con motivo "No hay registro de ingreso".
    Body: {"placa": "..."}
    """
    placa = str(request.data.get("placa", "")).strip().upper()
    if not placa:
        return Response({"detail": "Debe enviar 'placa'."}, status=status.HTTP_400_BAD_REQUEST)

    vehiculo = (
        Vehiculo.objects.filter(placa=placa)
        .select_related("propiedad", "visitante")
        .first()
    )
    if not vehiculo:
        return Response(
            {"permitido": False, "motivo": "Placa no registrada"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Residente: salida permitida
    if vehiculo.propiedad_id:
        return Response(
            {
                "permitido": True,
                "tipo": "residente",  # <- minúsculas para el test
                "placa": placa,
                "mensaje": "Salida permitida a residente",
            }
        )

    # Visitante
    if vehiculo.visitante_id:
        now = timezone.now()
        visita = (
            Visita.objects.filter(
                visitante=vehiculo.visitante,
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
                    "tipo": "Visitante",
                    "placa": placa,
                    "motivo": "No existe visita vigente",
                }
            )

        if visita.ingreso_real is None:
            # texto EXACTO que espera el test
            return Response(
                {
                    "permitido": False,
                    "tipo": "Visitante",
                    "placa": placa,
                    "visita_id": visita.id,
                    "motivo": "No hay registro de ingreso",
                }
            )

        if visita.salida_real is None:
            visita.salida_real = now
            visita.save(update_fields=["salida_real"])

        return Response(
            {
                "permitido": True,
                "tipo": "Visitante",
                "placa": placa,
                "visita_id": visita.id,
                "mensaje": "Salida registrada y visita cerrada",
            }
        )

    return Response(
        {"permitido": False, "motivo": "Vehículo sin asociación válida"},
        status=status.HTTP_403_FORBIDDEN,
    )

from datetime import date, datetime, time
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Visita

@api_view(["GET"])
@permission_classes([AllowAny])  # por ahora sin auth, como acordamos
def visitas_abiertas(request):
    """
    Lista visitas 'abiertas' (ingreso_real != null y salida_real == null).

    Filtros opcionales:
      - ?propiedad=<id>    -> solo esa propiedad
      - ?fecha=YYYY-MM-DD  -> por defecto: hoy (hora local)
    """
    tz = timezone.get_current_timezone()
    hoy = timezone.localdate()

    # fecha filtro (opcional)
    fecha_str = request.query_params.get("fecha")
    try:
        fecha = date.fromisoformat(fecha_str) if fecha_str else hoy
    except ValueError:
        fecha = hoy

    inicio_dia = datetime.combine(fecha, time.min, tzinfo=tz)
    fin_dia = datetime.combine(fecha, time.max, tzinfo=tz)

    qs = (
        Visita.objects
        .select_related("visitante", "propiedad")
        .filter(ingreso_real__isnull=False, salida_real__isnull=True)
        .filter(ingreso_real__lte=fin_dia)   # ya ingresó antes de terminar el día
        .order_by("-ingreso_real")
    )

    # filtro por propiedad (opcional)
    prop_id = request.query_params.get("propiedad")
    if prop_id:
        qs = qs.filter(propiedad_id=prop_id)

    data = [{
        "id": v.id,
        "visitante": ({
            "id": v.visitante_id,
            "nombre": v.visitante.nombre_completo,
            "documento": v.visitante.documento,
        } if v.visitante_id else None),
        "propiedad": ({
            "id": v.propiedad_id,
            "numero_casa": v.propiedad.numero_casa,
        } if v.propiedad_id else None),
        "ingreso_real": v.ingreso_real,
        "fecha_salida_programada": v.fecha_salida_programada,
    } for v in qs]

    return Response({"count": len(data), "results": data})

