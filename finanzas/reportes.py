# finanzas/reportes.py
from __future__ import annotations

import csv
import io
from datetime import datetime, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.core.exceptions import FieldDoesNotExist, FieldError

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Importa tus modelos reales
from finanzas.models import Gasto, Pago, PagoMulta  # Multa/Reserva no son necesarias aquí
from condominio.models import Propiedad


# ---------------------------
# Utilidades “a prueba de esquema”
# ---------------------------

def model_has_field(model, field_name: str) -> bool:
    try:
        model._meta.get_field(field_name)
        return True
    except FieldDoesNotExist:
        return False

def first_existing_field(model, candidates: list[str], default: str | None = None) -> str | None:
    for name in candidates:
        if model_has_field(model, name):
            return name
    return default

def safe_filter(qs, **kwargs):
    """Hace filter ignorando campos inexistentes (si el esquema difiere)."""
    try:
        return qs.filter(**kwargs)
    except FieldError:
        return qs  # sin filtrar


# ---------------------------
# Generación de PDF (ReportLab si está disponible)
# ---------------------------

def build_pdf_bytes(title: str, lines: list[str]) -> bytes | None:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        y = height - 50
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, title)
        y -= 20
        c.setFont("Helvetica", 11)
        for line in lines:
            if y < 60:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 11)
            c.drawString(40, y, line)
            y -= 16

        c.showPage()
        c.save()
        return buffer.getvalue()
    except Exception:
        # ReportLab no instalado u otro error → devolvemos None
        return None


# ---------------------------
# 1) Comprobante PDF de Pago
# ---------------------------

class ReciboPagoPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pago_id: int):
        try:
            pago = Pago.objects.select_related("gasto").get(pk=pago_id)
        except Pago.DoesNotExist:
            return Response({"detail": "Pago no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Campos tolerantes a esquema
        monto_field = "monto_pagado" if model_has_field(Pago, "monto_pagado") else first_existing_field(Pago, ["monto", "importe"], None)
        fecha_field = first_existing_field(Pago, ["fecha", "fecha_pago", "created_at", "creado_en"], None)

        monto_val: Decimal = getattr(pago, monto_field, None) if monto_field else None
        fecha_val = getattr(pago, fecha_field, None) if fecha_field else timezone.now()

        prop = None
        if getattr(pago, "gasto", None) and getattr(pago.gasto, "propiedad_id", None):
            try:
                prop = Propiedad.objects.get(pk=pago.gasto.propiedad_id)
            except Propiedad.DoesNotExist:
                prop = None

        title = "Comprobante de Pago"
        lines = [
            f"ID de pago: {pago.id}",
            f"Fecha: {fecha_val}",
            f"Monto: {monto_val if monto_val is not None else 'N/D'}",
            f"Gasto asociado: {getattr(pago, 'gasto_id', 'N/D')}",
            f"Propiedad: {prop.id if prop else 'N/D'}",
            "",
            "Este documento certifica que el pago ha sido registrado en el sistema.",
        ]

        pdf_bytes = build_pdf_bytes(title, lines)
        if not pdf_bytes:
            return Response(
                {"detail": "No se pudo generar el PDF (instala reportlab: pip install reportlab)."},
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )

        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = f'attachment; filename="comprobante_pago_{pago.id}.pdf"'
        return resp


# ---------------------------
# 1b) Comprobante PDF de PagoMulta
# ---------------------------

class ReciboPagoMultaPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pago_multa_id: int):
        try:
            pm = PagoMulta.objects.select_related("multa").get(pk=pago_multa_id)
        except PagoMulta.DoesNotExist:
            return Response({"detail": "Pago de multa no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        monto_field = "monto_pagado" if model_has_field(PagoMulta, "monto_pagado") else first_existing_field(PagoMulta, ["monto", "importe"], None)
        fecha_field = first_existing_field(PagoMulta, ["fecha", "fecha_pago", "created_at", "creado_en"], None)

        monto_val: Decimal = getattr(pm, monto_field, None) if monto_field else None
        fecha_val = getattr(pm, fecha_field, None) if fecha_field else timezone.now()

        title = "Comprobante de Pago de Multa"
        lines = [
            f"ID pago multa: {pm.id}",
            f"Fecha: {fecha_val}",
            f"Monto: {monto_val if monto_val is not None else 'N/D'}",
            f"Multa asociada: {getattr(pm, 'multa_id', 'N/D')}",
            "",
            "Este documento certifica que el pago de la multa ha sido registrado.",
        ]

        pdf_bytes = build_pdf_bytes(title, lines)
        if not pdf_bytes:
            return Response(
                {"detail": "No se pudo generar el PDF (instala reportlab: pip install reportlab)."},
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )

        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = f'attachment; filename="comprobante_pago_multa_{pm.id}.pdf"'
        return resp


# ---------------------------
# 2) Reporte de Morosidad (JSON o CSV)
# ---------------------------

class ReporteMorosidadView(APIView):
    """
    GET ?mes=9&anio=2025&fmt=csv|json (json por defecto)
    Calcula deuda = suma de Gasto.pagado=False por propiedad.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        mes = request.GET.get("mes")
        anio = request.GET.get("anio")
        fmt = (request.GET.get("fmt") or "json").lower()

        qs = Gasto.objects.all()
        # Filtrado tolerante (si existen esos campos en tu modelo)
        if mes:
            qs = safe_filter(qs, mes=int(mes))
        if anio:
            qs = safe_filter(qs, anio=int(anio))

        qs_no_pagado = safe_filter(qs, pagado=False)
        agg = (
            qs_no_pagado
            .values("propiedad_id")
            .annotate(deuda=Sum("monto"))
            .order_by("-deuda")
        )

        rows = []
        for item in agg:
            prop_id = item["propiedad_id"]
            deuda = item["deuda"] or Decimal("0")
            rows.append({"propiedad_id": prop_id, "deuda": str(deuda)})

        if fmt == "csv":
            resp = HttpResponse(content_type="text/csv")
            resp["Content-Disposition"] = 'attachment; filename="reporte_morosidad.csv"'
            w = csv.writer(resp)
            w.writerow(["propiedad_id", "deuda"])
            for r in rows:
                w.writerow([r["propiedad_id"], r["deuda"]])
            return resp

        return JsonResponse({"result": rows})


# ---------------------------
# 2b) Resumen financiero (JSON o CSV)
# ---------------------------

class ReporteResumenView(APIView):
    """
    GET ?desde=YYYY-MM-DD&hasta=YYYY-MM-DD&fmt=csv|json
    Suma ingresos de Pagos y Pagos de Multa en el rango (si hay campo fecha),
    y expone conteos básicos de gastos emitidos.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        fmt = (request.GET.get("fmt") or "json").lower()

        # Rango por defecto: últimos 30 días
        try:
            desde = datetime.fromisoformat(request.GET.get("desde")) if request.GET.get("desde") else timezone.now() - timedelta(days=30)
            hasta = datetime.fromisoformat(request.GET.get("hasta")) if request.GET.get("hasta") else timezone.now()
        except ValueError:
            return Response({"detail": "Formato de fecha inválido (usa YYYY-MM-DD)."}, status=status.HTTP_400_BAD_REQUEST)

        # Campos de fecha tolerantes
        pago_date_field = first_existing_field(Pago, ["fecha", "fecha_pago", "created_at", "creado_en"])
        pago_multa_date_field = first_existing_field(PagoMulta, ["fecha", "fecha_pago", "created_at", "creado_en"])

        # Ingresos por cuotas
        monto_field_pago = "monto_pagado" if model_has_field(Pago, "monto_pagado") else first_existing_field(Pago, ["monto", "importe"])
        pagos_qs = Pago.objects.all()
        if pago_date_field:
            pagos_qs = safe_filter(pagos_qs, **{f"{pago_date_field}__date__gte": desde.date()})
            pagos_qs = safe_filter(pagos_qs, **{f"{pago_date_field}__date__lte": hasta.date()})

        total_pagos = pagos_qs.aggregate(total=Sum(monto_field_pago or "id")).get("total") or Decimal("0")

        # Ingresos por multas
        monto_field_pm = "monto_pagado" if model_has_field(PagoMulta, "monto_pagado") else first_existing_field(PagoMulta, ["monto", "importe"])
        pagos_multas_qs = PagoMulta.objects.all()
        if pago_multa_date_field:
            pagos_multas_qs = safe_filter(pagos_multas_qs, **{f"{pago_multa_date_field}__date__gte": desde.date()})
            pagos_multas_qs = safe_filter(pagos_multas_qs, **{f"{pago_multa_date_field}__date__lte": hasta.date()})

        total_pagos_multas = pagos_multas_qs.aggregate(total=Sum(monto_field_pm or "id")).get("total") or Decimal("0")

        # Gastos emitidos en rango (si tu Gasto tiene campos de fecha; sino, se devuelve el total global)
        gasto_date_field = first_existing_field(Gasto, ["fecha_emision", "fecha", "created_at", "creado_en"])
        gastos_qs = Gasto.objects.all()
        if gasto_date_field:
            gastos_qs = safe_filter(gastos_qs, **{f"{gasto_date_field}__date__gte": desde.date()})
            gastos_qs = safe_filter(gastos_qs, **{f"{gasto_date_field}__date__lte": hasta.date()})

        total_gastos_emitidos = gastos_qs.aggregate(total=Sum("monto")).get("total") or Decimal("0")

        data = {
            "desde": desde.date().isoformat(),
            "hasta": hasta.date().isoformat(),
            "ingresos_cuotas": str(total_pagos),
            "ingresos_multas": str(total_pagos_multas),
            "ingresos_totales": str((total_pagos or 0) + (total_pagos_multas or 0)),
            "gastos_emitidos": str(total_gastos_emitidos),
        }

        if fmt == "csv":
            resp = HttpResponse(content_type="text/csv")
            resp["Content-Disposition"] = 'attachment; filename="reporte_resumen.csv"'
            w = csv.writer(resp)
            w.writerow(list(data.keys()))
            w.writerow(list(data.values()))
            return resp

        return JsonResponse(data)
