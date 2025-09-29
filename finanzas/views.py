from datetime import datetime, timedelta, date
from decimal import Decimal
import io
import csv
import json # Importa json para formatear la descripción

# finanzas/views.py

from django.db.models import Sum, Count, F, ExpressionWrapper, fields, Q
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.utils import timezone

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .reportes import generar_reporte_financiero_pdf
from condominio.models import Propiedad
from .models import Gasto, Pago, Multa, PagoMulta, Reserva, Egreso, Ingreso
from .serializers import (
    GastoSerializer, PagoSerializer, MultaSerializer,
    PagoMultaSerializer, ReservaSerializer,EgresoSerializer, IngresoSerializer
)
from .services import simular_pago_qr, iniciar_pago_qr

from auditoria.services import registrar_evento

def _ip(request):
    return getattr(request, "ip_address", request.META.get("REMOTE_ADDR"))

def format_description(data):
    """Convierte un diccionario a un string JSON para la bitácora."""
    return json.dumps(data, indent=4, default=str)

# =========================
#        GASTOS
# =========================
class GastoViewSet(viewsets.ModelViewSet):
    queryset = Gasto.objects.select_related('propiedad').all()
    serializer_class = GastoSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='crear_mensual', permission_classes=[IsAdminUser])
    def crear_mensual(self, request):
        # ... (lógica de la función sin cambios) ...
        descripcion = (request.data.get('descripcion') or '').strip()
        monto_raw = request.data.get('monto')
        fecha_str = request.data.get('fecha') or request.data.get('fecha_emision')
        venc_str = request.data.get('fecha_vencimiento')

        if not monto_raw:
            return Response({'detail': 'monto es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            monto = float(monto_raw)
            if monto <= 0:
                return Response({'detail': 'monto debe ser > 0.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'detail': 'monto inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        if fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({'detail': 'fecha inválida. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            fecha = timezone.now().date()

        fecha_vencimiento = None
        if venc_str:
            try:
                fecha_vencimiento = datetime.strptime(venc_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({'detail': 'fecha_vencimiento inválida. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        mes, anio = fecha.month, fecha.year
        creados, duplicados, errores = 0, [], []

        for prop in Propiedad.objects.all():
            try:
                Gasto.objects.create(
                    propiedad=prop,
                    monto=monto,
                    fecha_emision=fecha,
                    fecha_vencimiento=fecha_vencimiento,
                    descripcion=descripcion,
                    pagado=False,
                    mes=mes, anio=anio,
                )
                creados += 1
            except IntegrityError:
                duplicados.append(prop.id)
            except Exception as e:
                errores.append({'propiedad_id': prop.id, 'error': str(e)})

        # --- CORRECCIÓN DE AUDITORÍA ---
        registrar_evento(
            usuario=request.user,
            accion="Creación Masiva de Gastos Mensuales",
            ip_address=_ip(request),
            descripcion=format_description({
                "mes": mes, "año": anio, "monto_individual": monto,
                "gastos_creados": creados, "propiedades_duplicadas": duplicados,
                "errores": errores
            })
        )
        # --- FIN CORRECCIÓN ---

        payload = {
            'status': f'Gastos creados: {creados}',
            'mes': mes, 'anio': anio,
            'duplicados': duplicados, 'errores': errores
        }
        return Response(payload, status=status.HTTP_201_CREATED if creados else status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='registrar_pago')
    def registrar_pago(self, request, pk=None):
        gasto = self.get_object()
        monto_raw = request.data.get('monto_pagado') or gasto.monto
        try:
            monto = Decimal(str(monto_raw))
        except Exception:
            return Response({'detail': 'monto_pagado inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            pago = Pago.objects.create(
                gasto=gasto,
                usuario=request.user if request.user.is_authenticated else None,
                monto_pagado=monto,
            )
            gasto.pagado = True
            gasto.save(update_fields=['pagado'])
            
            # --- CORRECCIÓN DE AUDITORÍA ---
            registrar_evento(
                usuario=request.user,
                accion="Registro de Pago Individual",
                ip_address=_ip(request),
                descripcion=format_description({
                    "pago_id": pago.id, "gasto_id": gasto.id,
                    "monto_pagado": str(monto), "propiedad_id": gasto.propiedad.id
                })
            )
            # --- FIN CORRECCIÓN ---

        return Response(PagoSerializer(pago).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='pagar_en_lote')
    def pagar_en_lote(self, request):
        ids = request.data.get('ids') or []
        if not isinstance(ids, list) or not ids:
            return Response({'detail': 'Proporcione una lista "ids".'}, status=status.HTTP_400_BAD_REQUEST)
        
        hechos, ya_pagados, no_encontrados = 0, [], []
        pagos_creados_ids = []
        
        for gid in ids:
            try:
                gasto = Gasto.objects.get(pk=gid)
            except Gasto.DoesNotExist:
                no_encontrados.append(gid)
                continue
            if gasto.pagado:
                ya_pagados.append(gid)
                continue
            pago = Pago.objects.create(
                gasto=gasto,
                usuario=request.user if request.user.is_authenticated else None,
                monto_pagado=gasto.monto,
            )
            gasto.pagado = True
            gasto.save(update_fields=['pagado'])
            hechos += 1
            pagos_creados_ids.append(pago.id)

        # --- CORRECCIÓN DE AUDITORÍA ---
        registrar_evento(
            usuario=request.user,
            accion="Registro de Pago en Lote",
            ip_address=_ip(request),
            descripcion=format_description({
                "gastos_solicitados_ids": ids,
                "gastos_pagados_count": hechos,
                "pagos_creados_ids": pagos_creados_ids,
                "gastos_ya_pagados_ids": ya_pagados,
                "gastos_no_encontrados_ids": no_encontrados
            })
        )
        # --- FIN CORRECCIÓN ---

        return Response({'pagados': hechos, 'ya_pagados': ya_pagados}, status=status.HTTP_201_CREATED)


# =========================
#         MULTAS
# =========================
class MultaViewSet(viewsets.ModelViewSet):
    queryset = Multa.objects.select_related('propiedad').all()
    serializer_class = MultaSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        multa = serializer.save()
        # --- CORRECCIÓN DE AUDITORÍA ---
        registrar_evento(
            usuario=self.request.user,
            accion="Creación de Multa",
            ip_address=_ip(self.request),
            descripcion=format_description({
                "multa_id": multa.id,
                "propiedad_id": multa.propiedad.id,
                "monto": str(multa.monto),
                "motivo": multa.motivo,
            })
        )
        # --- FIN CORRECCIÓN ---

    @action(detail=True, methods=['post'], url_path='registrar_pago')
    def registrar_pago(self, request, pk=None):
        multa = self.get_object()
        monto_raw = request.data.get('monto_pagado') or multa.monto
        try:
            monto = Decimal(str(monto_raw))
        except Exception:
            return Response({'detail': 'monto_pagado inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            pago = PagoMulta.objects.create(
                multa=multa,
                usuario=request.user if request.user.is_authenticated else None,
                monto_pagado=monto,
            )
            multa.pagado = True
            multa.save(update_fields=['pagado'])
            
            # --- CORRECCIÓN DE AUDITORÍA ---
            registrar_evento(
                usuario=request.user,
                accion="Registro de Pago de Multa Individual",
                ip_address=_ip(request),
                descripcion=format_description({
                    "pago_multa_id": pago.id, "multa_id": multa.id,
                    "monto_pagado": str(monto)
                })
            )
            # --- FIN CORRECCIÓN ---

        return Response(PagoMultaSerializer(pago).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='pagar_en_lote')
    def pagar_en_lote(self, request):
        ids = request.data.get('ids') or []
        if not isinstance(ids, list) or not ids:
            return Response({'detail': 'Proporcione una lista "ids".'}, status=status.HTTP_400_BAD_REQUEST)

        hechos, ya_pagados, no_encontrados = 0, [], []
        pagos_multa_creados_ids = []

        for mid in ids:
            try:
                multa = Multa.objects.get(pk=mid)
            except Multa.DoesNotExist:
                no_encontrados.append(mid)
                continue
            if multa.pagado:
                ya_pagados.append(mid)
                continue
            pago = PagoMulta.objects.create(
                multa=multa,
                usuario=request.user if request.user.is_authenticated else None,
                monto_pagado=multa.monto,
            )
            multa.pagado = True
            multa.save(update_fields=['pagado'])
            hechos += 1
            pagos_multa_creados_ids.append(pago.id)

        # --- CORRECCIÓN DE AUDITORÍA ---
        registrar_evento(
            usuario=request.user,
            accion="Registro de Pago de Multas en Lote",
            ip_address=_ip(request),
            descripcion=format_description({
                "multas_solicitadas_ids": ids,
                "multas_pagadas_count": hechos,
                "pagos_multa_creados_ids": pagos_multa_creados_ids,
                "multas_ya_pagadas_ids": ya_pagados,
                "multas_no_encontradas_ids": no_encontrados
            })
        )
        # --- FIN CORRECCIÓN ---

        return Response({'pagados': hechos, 'ya_pagados': ya_pagados}, status=status.HTTP_201_CREATED)


# =========================
#        PAGOS (listas)
# =========================
class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.select_related('gasto', 'usuario').all()
    serializer_class = PagoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        pago = serializer.save(usuario=self.request.user)
        # --- CORRECCIÓN DE AUDITORÍA ---
        registrar_evento(
            usuario=self.request.user,
            accion="Creación de Objeto de Pago (Genérico)",
            ip_address=_ip(self.request),
            descripcion=format_description({
                "pago_id": pago.id, 
                "gasto_id": pago.gasto.id if pago.gasto else None, 
                "monto": str(pago.monto_pagado)
            })
        )
        # --- FIN CORRECCIÓN ---

class PagoMultaViewSet(viewsets.ModelViewSet):
    queryset = PagoMulta.objects.select_related('multa', 'usuario').all()
    serializer_class = PagoMultaSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        pago_multa = serializer.save(usuario=self.request.user)
        # --- CORRECCIÓN DE AUDITORÍA ---
        registrar_evento(
            usuario=self.request.user,
            accion="Creación de Objeto de Pago de Multa (Genérico)",
            ip_address=_ip(self.request),
            descripcion=format_description({
                "pago_multa_id": pago_multa.id, 
                "multa_id": pago_multa.multa.id if pago_multa.multa else None, 
                "monto": str(pago_multa.monto_pagado)
            })
        )
        # --- FIN CORRECCIÓN ---

# ... (El resto del archivo views.py permanece igual)
# =========================
#        RESERVAS
# =========================
class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.select_related('area_comun', 'usuario').all()
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        reserva = serializer.save(usuario=self.request.user)
        # --- CORRECCIÓN DE AUDITORÍA ---
        registrar_evento(
            usuario=self.request.user,
            accion="Creación de Reserva",
            ip_address=_ip(self.request),
            descripcion=format_description({
                "reserva_id": reserva.id, "area_comun_id": reserva.area_comun.id,
                "fecha_reserva": reserva.fecha_reserva.isoformat()
            })
        )
        # --- FIN CORRECCIÓN ---


# ------------ Comprobantes (PDF con fallback a TXT) ------------
class _ReciboBase:
    @staticmethod
    def build_pdf(title: str, lines: list[str]) -> bytes | None:
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter

            buf = io.BytesIO()
            c = canvas.Canvas(buf, pagesize=letter)
            w, h = letter
            y = h - 72
            c.setFont("Helvetica-Bold", 16)
            c.drawString(72, y, title)
            y -= 28
            c.setFont("Helvetica", 12)
            for line in lines:
                c.drawString(72, y, str(line))
                y -= 18
            c.showPage()
            c.save()
            pdf = buf.getvalue()
            buf.close()
            return pdf
        except Exception:
            return None


class ReciboPagoPDFView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pago_id: int, *args, **kwargs):
        title = f"Recibo de pago #{pago_id}"
        lines = []
        try:
            p = Pago.objects.get(pk=pago_id)
            monto = getattr(p, "monto_pagado", None) or getattr(p, "monto", None)
            fecha = getattr(p, "fecha_pago", None) or getattr(p, "fecha", None)
            lines += [f"Monto: {monto}", f"Fecha: {fecha}"]
        except Pago.DoesNotExist:
            lines.append("Pago no encontrado (recibo de demostración).")

        pdf = _ReciboBase.build_pdf(title, lines)
        if pdf:
            resp = HttpResponse(pdf, content_type="application/pdf")
            resp["Content-Disposition"] = f'attachment; filename="recibo_pago_{pago_id}.pdf"'
            return resp

        resp = HttpResponse(f"{title}\n" + "\n".join(lines), content_type="text/plain; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="recibo_pago_{pago_id}.txt"'
        return resp


class ReciboPagoMultaPDFView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pago_multa_id: int, *args, **kwargs):
        title = f"Recibo de pago de multa #{pago_multa_id}"
        lines = []
        try:
            pm = PagoMulta.objects.get(pk=pago_multa_id)
            monto = getattr(pm, "monto_pagado", None) or getattr(pm, "monto", None)
            fecha = getattr(pm, "fecha_pago", None) or getattr(pm, "fecha", None)
            lines += [f"Monto: {monto}", f"Fecha: {fecha}"]
        except PagoMulta.DoesNotExist:
            lines.append("Pago de multa no encontrado (recibo de demostración).")

        pdf = _ReciboBase.build_pdf(title, lines)
        if pdf:
            resp = HttpResponse(pdf, content_type="application/pdf")
            resp["Content-Disposition"] = f'attachment; filename="recibo_pago_multa_{pago_multa_id}.pdf"'
            return resp

        resp = HttpResponse(f"{title}\n" + "\n".join(lines), content_type="text/plain; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="recibo_pago_multa_{pago_multa_id}.txt"'
        return resp


# ------------ Reportes (plantillas funcionales) ------------
class ReporteMorosidadView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        mes = request.query_params.get("mes")
        anio = request.query_params.get("anio")
        fmt = (request.query_params.get("fmt") or "json").lower()
        data = []
        if fmt == "csv":
            resp = HttpResponse(content_type="text/csv")
            resp["Content-Disposition"] = 'attachment; filename="estado_morosidad.csv"'
            w = csv.writer(resp)
            w.writerow(["propiedad_id", "deuda"])
            for row in data:
                w.writerow(row)
            return resp
        return Response({"mes": mes, "anio": anio, "items": data})


class ReporteResumenView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        desde = request.query_params.get("desde")
        hasta = request.query_params.get("hasta")
        return Response({"desde": desde, "hasta": hasta, "ingresos": 0, "egresos": 0})


# ------------ Pagos con pasarela (demo) ------------
class IniciarPagoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pago_id, *args, **kwargs):
        resultado = iniciar_pago_qr(pago_id)
        if "error" in resultado:
            return Response(resultado, status=status.HTTP_400_BAD_REQUEST)
        return Response(resultado, status=status.HTTP_200_OK)


class SimularPagoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pago_id, *args, **kwargs):
        try:
            pago = Pago.objects.select_related('gasto', 'reserva').get(id=pago_id, usuario=request.user)
        except Pago.DoesNotExist:
            return Response({"error": "Pago no encontrado o no te pertenece."}, status=status.HTTP_404_NOT_FOUND)

        if getattr(pago, "estado_pago", "") == "PAGADO":
            return Response({"mensaje": "Este pago ya fue realizado."}, status=status.HTTP_400_BAD_REQUEST)

        data = simular_pago_qr(pago.id)
        if "error" in data:
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        pago.refresh_from_db()
        if getattr(pago, "gasto_id", None):
            pago.gasto.pagado = True
            pago.gasto.save(update_fields=["pagado"])
        if getattr(pago, "reserva_id", None):
            pago.reserva.pagada = True
            pago.reserva.save(update_fields=["pagada"])

        return Response({
            "mensaje": data.get("mensaje", "Pago simulado y confirmado exitosamente."),
            "pago_id": pago.id,
            "estado": pago.estado_pago
        }, status=status.HTTP_200_OK)



class WebhookConfirmacionPagoView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        pago_id_externo = data.get('idExterno')
        estado_transaccion = data.get('estado')
        
        # --- CORRECCIÓN DE AUDITORÍA ---
        registrar_evento(
            usuario=None,
            accion="Webhook de Pasarela Recibido",
            ip_address=_ip(request),
            descripcion=format_description({"payload_recibido": data})
        )
        # --- FIN CORRECCIÓN ---

        try:
            pago = Pago.objects.get(id=int(pago_id_externo))
            if estado_transaccion == 'PAGADO':
                pago.estado_pago = 'PAGADO'
                pago.save(update_fields=["estado_pago"])
            else:
                pago.estado_pago = 'FALLIDO'
                pago.save(update_fields=["estado_pago"])
        except (Pago.DoesNotExist, ValueError, TypeError):
            pass

        return Response(status=status.HTTP_200_OK)


class PagarReservaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, reserva_id, *args, **kwargs):
        try:
            reserva = Reserva.objects.get(id=reserva_id, usuario=request.user)
        except Reserva.DoesNotExist:
            return Response({"detail": "Reserva no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        if getattr(reserva, "pagada", False):
            return Response({"detail": "Esta reserva ya fue pagada."}, status=status.HTTP_400_BAD_REQUEST)

        pago = Pago.objects.create(
            reserva=reserva,
            usuario=request.user,
            monto_pagado=reserva.costo_total,
            estado_pago='PENDIENTE'
        )

        data = simular_pago_qr(pago.id)
        if "error" in data:
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        reserva.pagada = True
        reserva.save(update_fields=["pagada"])

        return Response({
            "mensaje": data.get("mensaje", "Pago de reserva simulado con éxito."),
            "pago_id": pago.id
        }, status=status.HTTP_200_OK)

# ------------ Utilidades admin / estado de cuenta ------------
class GenerarExpensasView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        monto = request.data.get('monto')
        descripcion = request.data.get('descripcion')
        fecha_vencimiento = request.data.get('fecha_vencimiento')
        if not all([monto, descripcion, fecha_vencimiento]):
            return Response({"error": "Monto, descripción y fecha_vencimiento son requeridos."},
                             status=status.HTTP_400_BAD_REQUEST)

        creados = 0
        gastos_creados_ids = []
        for propiedad in Propiedad.objects.all():
            gasto = Gasto.objects.create(
                propiedad=propiedad,
                monto=monto,
                fecha_emision=date.today(),
                fecha_vencimiento=fecha_vencimiento,
                descripcion=descripcion,
                pagado=False
            )
            creados += 1
            gastos_creados_ids.append(gasto.id)

        # --- CORRECCIÓN DE AUDITORÍA ---
        registrar_evento(
            usuario=request.user,
            accion="Generación Manual de Expensas",
            ip_address=_ip(request),
            descripcion=format_description({
                "gastos_creados_count": creados,
                "gastos_ids": gastos_creados_ids,
                "monto_individual": monto,
                "descripcion": descripcion
            })
        )
        # --- FIN CORRECCIÓN ---

        return Response({"mensaje": f"{creados} gastos de expensas generados."}, status=status.HTTP_201_CREATED)

class EstadoDeCuentaView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # ... (lógica sin cambios) ...
        usuario = request.user
        gastos_pendientes = (
            Gasto.objects
            .filter(
                Q(propiedad__propietario=usuario) |
                Q(propiedad__residentes__usuario=usuario),
                pagado=False
            )
            .distinct()
        )
        multas_pendientes = (
            Multa.objects
            .filter(
                Q(propiedad__propietario=usuario) |
                Q(propiedad__residentes__usuario=usuario),
                pagado=False
            )
            .distinct()
        )
        reservas_pendientes = (
            Reserva.objects
            .filter(usuario=usuario, pagada=False)
            .distinct()
        )
        gastos_data = GastoSerializer(gastos_pendientes, many=True).data
        for item in gastos_data:
            item['tipo_deuda'] = 'gasto'
        multas_data = MultaSerializer(multas_pendientes, many=True).data
        for item in multas_data:
            item['tipo_deuda'] = 'multa'
        reservas_data = ReservaSerializer(reservas_pendientes, many=True).data
        for item in reservas_data:
            item['tipo_deuda'] = 'reserva'
        deudas_combinadas = gastos_data + multas_data + reservas_data
        return Response(deudas_combinadas)


class EgresoViewSet(viewsets.ModelViewSet):
    queryset = Egreso.objects.all()
    serializer_class = EgresoSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        egreso = serializer.save()
        # --- CORRECCIÓN DE AUDITORÍA ---
        registrar_evento(
            usuario=self.request.user,
            accion="Registro de Egreso",
            ip_address=_ip(self.request),
            descripcion=format_description({"egreso_id": egreso.id, "monto": str(egreso.monto), "categoria": egreso.categoria})
        )
        # --- FIN CORRECCIÓN ---

class IngresoViewSet(viewsets.ModelViewSet):
    queryset = Ingreso.objects.all()
    serializer_class = IngresoSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        ingreso = serializer.save()
        # --- CORRECCIÓN DE AUDITORÍA ---
        registrar_evento(
            usuario=self.request.user,
            accion="Registro de Ingreso Manual",
            ip_address=_ip(self.request),
            descripcion=format_description({"ingreso_id": ingreso.id, "monto": str(ingreso.monto), "concepto": ingreso.concepto})
        )
        # --- FIN CORRECCIÓN ---


# ========= NUEVA VISTA PARA REPORTE FINANCIERO =========

class ReporteFinancieroView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get_financial_data(self, request):
        # ... (lógica sin cambios) ...
        try:
            fecha_fin_str = request.query_params.get('fecha_fin', date.today().isoformat())
            fecha_fin = date.fromisoformat(fecha_fin_str)
            fecha_inicio_str = request.query_params.get('fecha_inicio', (fecha_fin - timedelta(days=30)).isoformat())
            fecha_inicio = date.fromisoformat(fecha_inicio_str)
            if fecha_inicio > fecha_fin:
                return None, Response({"error": "La fecha de inicio no puede ser posterior a la fecha de fin."}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return None, Response({"error": "Formato de fecha inválido. Use AAAA-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        ingresos_qs = Ingreso.objects.filter(fecha__range=[fecha_inicio, fecha_fin])
        total_ingresos = ingresos_qs.aggregate(total=Sum('monto'))['total'] or 0
        ingresos_por_concepto = list(ingresos_qs.values('concepto').annotate(subtotal=Sum('monto')).order_by('-subtotal'))

        egresos_qs = Egreso.objects.filter(fecha__range=[fecha_inicio, fecha_fin])
        total_egresos = egresos_qs.aggregate(total=Sum('monto'))['total'] or 0
        egresos_por_categoria = list(egresos_qs.values('categoria').annotate(subtotal=Sum('monto')).order_by('-subtotal'))

        balance = total_ingresos - total_egresos

        data = {
            'rango_fechas': {'inicio': fecha_inicio.isoformat(), 'fin': fecha_fin.isoformat()},
            'resumen': {'total_ingresos': total_ingresos, 'total_egresos': total_egresos, 'balance': balance},
            'detalle_ingresos': ingresos_por_concepto,
            'detalle_egresos': egresos_por_categoria,
        }
        return data, None

    def get(self, request, *args, **kwargs):
        formato = request.query_params.get('formato', 'json').lower()
        
        data, error_response = self.get_financial_data(request)
        if error_response:
            return error_response
            
        # --- CORRECCIÓN DE AUDITORÍA ---
        registrar_evento(
            usuario=request.user,
            accion="Generación de Reporte Financiero",
            ip_address=_ip(request),
            descripcion=format_description({"rango_fechas": data['rango_fechas'], "formato": formato})
        )
        # --- FIN CORRECCIÓN ---

        if formato == 'pdf':
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="reporte_financiero_{data["rango_fechas"]["inicio"]}_a_{data["rango_fechas"]["fin"]}.pdf"'
            
            return generar_reporte_financiero_pdf(response, data)
        
        return Response(data, status=status.HTTP_200_OK)
    


class ReporteUsoAreasComunesView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        # ... (lógica sin cambios) ...
        try:
            fecha_fin_str = request.query_params.get('fecha_fin', date.today().isoformat())
            fecha_fin = date.fromisoformat(fecha_fin_str)

            fecha_inicio_str = request.query_params.get('fecha_inicio', (fecha_fin - timedelta(days=30)).isoformat())
            fecha_inicio = date.fromisoformat(fecha_inicio_str)

            if fecha_inicio > fecha_fin:
                return Response(
                    {"error": "La fecha de inicio no puede ser posterior a la fecha de fin."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {"error": "Formato de fecha inválido. Use AAAA-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        reservas_en_rango = Reserva.objects.filter(
            fecha_reserva__range=[fecha_inicio, fecha_fin],
            pagada=True
        )

        duracion_horas = ExpressionWrapper(
            (F('hora_fin') - F('hora_inicio')),
            output_field=fields.DurationField()
        )

        estadisticas = (
            reservas_en_rango
            .annotate(nombre_area=F('area_comun__nombre'))
            .values('nombre_area')
            .annotate(
                cantidad_reservas=Count('id'),
                total_horas_reservadas=Sum(duracion_horas),
                ingresos_generados=Sum('costo_total')
            )
            .order_by('-cantidad_reservas')
        )

        reporte_data = []
        for item in estadisticas:
            total_segundos = item['total_horas_reservadas'].total_seconds() if item['total_horas_reservadas'] else 0
            horas = round(total_segundos / 3600, 2)

            reporte_data.append({
                "area_comun": item['nombre_area'],
                "cantidad_reservas": item['cantidad_reservas'],
                "total_horas_reservadas": horas,
                "ingresos_generados": item['ingresos_generados'] or 0
            })

        data = {
            'rango_fechas': {
                'inicio': fecha_inicio.isoformat(),
                'fin': fecha_fin.isoformat(),
            },
            'reporte': reporte_data
        }

        # --- CORRECCIÓN DE AUDITORÍA ---
        registrar_evento(
            usuario=request.user,
            accion="Consulta de Reporte de Uso de Áreas Comunes",
            ip_address=_ip(request),
            descripcion=format_description({"rango_fechas": data['rango_fechas']})
        )
        # --- FIN CORRECCIÓN ---

        return Response(data, status=status.HTTP_200_OK)