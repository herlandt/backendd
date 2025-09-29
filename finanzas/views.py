from datetime import datetime, timedelta, date
from decimal import Decimal
import io
import csv
# finanzas/views.py

# ... (otras importaciones) ...
from django.db.models import Sum, Count, F, ExpressionWrapper, fields # <--- AÑADE O COMPLETA ESTA LÍNEA
# ... (el resto de las importaciones) ...
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
from .services import simular_pago_qr

from auditoria.services import registrar_evento

def _ip(request):
    # Usa la IP del middleware si existe; si no, REMOTE_ADDR como fallback.
    return getattr(request, "ip_address", request.META.get("REMOTE_ADDR"))

# =========================
#        GASTOS
# =========================
class GastoViewSet(viewsets.ModelViewSet):
    queryset = Gasto.objects.select_related('propiedad').all()
    serializer_class = GastoSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='crear_mensual', permission_classes=[IsAdminUser])
    def crear_mensual(self, request):
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

        return Response(PagoSerializer(pago).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='pagar_en_lote')
    def pagar_en_lote(self, request):
        ids = request.data.get('ids') or []
        if not isinstance(ids, list) or not ids:
            return Response({'detail': 'Proporcione una lista "ids".'}, status=status.HTTP_400_BAD_REQUEST)

        hechos, ya_pagados = 0, []
        for gid in ids:
            try:
                gasto = Gasto.objects.get(pk=gid)
            except Gasto.DoesNotExist:
                continue
            if gasto.pagado:
                ya_pagados.append(gid)
                continue
            Pago.objects.create(
                gasto=gasto,
                usuario=request.user if request.user.is_authenticated else None,
                monto_pagado=gasto.monto,
            )
            gasto.pagado = True
            gasto.save(update_fields=['pagado'])
            hechos += 1

        return Response({'pagados': hechos, 'ya_pagados': ya_pagados}, status=status.HTTP_201_CREATED)


# =========================
#        MULTAS
# =========================
class MultaViewSet(viewsets.ModelViewSet):
    queryset = Multa.objects.select_related('propiedad').all()
    serializer_class = MultaSerializer
    permission_classes = [IsAuthenticated]

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

        return Response(PagoMultaSerializer(pago).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='pagar_en_lote')
    def pagar_en_lote(self, request):
        ids = request.data.get('ids') or []
        if not isinstance(ids, list) or not ids:
            return Response({'detail': 'Proporcione una lista "ids".'}, status=status.HTTP_400_BAD_REQUEST)

        hechos, ya_pagados = 0, []
        for mid in ids:
            try:
                multa = Multa.objects.get(pk=mid)
            except Multa.DoesNotExist:
                continue
            if multa.pagado:
                ya_pagados.append(mid)
                continue
            PagoMulta.objects.create(
                multa=multa,
                usuario=request.user if request.user.is_authenticated else None,
                monto_pagado=multa.monto,
            )
            multa.pagado = True
            multa.save(update_fields=['pagado'])
            hechos += 1

        return Response({'pagados': hechos, 'ya_pagados': ya_pagados}, status=status.HTTP_201_CREATED)


# =========================
#        PAGOS (listas)
# =========================
class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.select_related('gasto', 'usuario').all()
    serializer_class = PagoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class PagoMultaViewSet(viewsets.ModelViewSet):
    queryset = PagoMulta.objects.select_related('multa', 'usuario').all()
    serializer_class = PagoMultaSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


# =========================
#        RESERVAS
# =========================
class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.select_related('area_comun', 'usuario').all()
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


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
    permission_classes = [AllowAny]  # déjalo abierto para probar fácil

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

        data = []  # aquí luego metes la lógica real

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
        # 1) El pago debe ser del usuario autenticado
        try:
            pago = Pago.objects.select_related('gasto', 'reserva').get(id=pago_id, usuario=request.user)
        except Pago.DoesNotExist:
            return Response({"error": "Pago no encontrado o no te pertenece."}, status=status.HTTP_404_NOT_FOUND)

        # 2) Si ya está pagado, no repetir
        if getattr(pago, "estado_pago", "") == "PAGADO":
            return Response({"mensaje": "Este pago ya fue realizado."}, status=status.HTTP_400_BAD_REQUEST)

        # 3) Llamar a TU servicio simulado
        data = simular_pago_qr(pago_id)
        if "error" in data:
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        # 4) Refrescar y marcar deudas como pagadas
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
    permission_classes = [AllowAny]  # debe ser público para la pasarela

    def post(self, request, *args, **kwargs):
        data = request.data
        pago_id_externo = data.get('idExterno')
        estado_transaccion = data.get('estado')

        try:
            pago = Pago.objects.get(id=int(pago_id_externo))
            if estado_transaccion == 'PAGADO':
                pago.estado_pago = 'PAGADO'
                pago.save(update_fields=["estado_pago"])
                # aquí podrías emitir notificación push
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

        # Crear un Pago pendiente para esa reserva
        pago = Pago.objects.create(
            reserva=reserva,
            usuario=request.user,
            monto_pagado=reserva.costo_total,
            estado_pago='PENDIENTE'
        )

        # Simular pago ahora mismo
        data = simular_pago_qr(pago.id)
        if "error" in data:
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        # Asegurar que quede marcada la reserva como pagada
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
        for propiedad in Propiedad.objects.all():
            Gasto.objects.create(
                propiedad=propiedad,
                monto=monto,
                fecha_emision=date.today(),
                fecha_vencimiento=fecha_vencimiento,
                descripcion=descripcion,
                pagado=False
            )
            creados += 1

        return Response({"mensaje": f"{creados} gastos de expensas generados."}, status=status.HTTP_201_CREATED)

# En finanzas/views.py

# ... (tus otras importaciones y vistas se quedan igual)
# finanzas/views.py# finanzas/views.py
from django.db.models import Q
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Gasto, Multa, Reserva
from .serializers import GastoSerializer, MultaSerializer, ReservaSerializer

class EstadoDeCuentaView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        usuario = request.user

        # Gastos pendientes del propietario o de residentes vinculados
        gastos_pendientes = (
            Gasto.objects
            .filter(
                Q(propiedad__propietario=usuario) |
                Q(propiedad__residentes__usuario=usuario),
                pagado=False
            )
            .distinct()
        )

        # (Opcional pero recomendado) incluir MULTAS pendientes
        multas_pendientes = (
            Multa.objects
            .filter(
                Q(propiedad__propietario=usuario) |
                Q(propiedad__residentes__usuario=usuario),
                pagado=False
            )
            .distinct()
        )

        # Reservas pendientes tal como ya lo tenías
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
    """
    API endpoint para la gestión de egresos del condominio.
    Solo accesible por administradores.
    """
    queryset = Egreso.objects.all()
    serializer_class = EgresoSerializer
    permission_classes = [permissions.IsAdminUser] # Solo admins pueden gestionar egresos

class IngresoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para la gestión de ingresos del condominio.
    Permite ver todos los ingresos y agregar ingresos manuales.
    """
    queryset = Ingreso.objects.all()
    serializer_class = IngresoSerializer
    permission_classes = [permissions.IsAdminUser] # Solo admins pueden gestionar ingresos




# ========= NUEVA VISTA PARA REPORTE FINANCIERO =========

class ReporteFinancieroView(APIView):
    """
    Genera un reporte financiero con un resumen de ingresos y egresos
    dentro de un rango de fechas.
    Soporta dos formatos: JSON (defecto) y PDF (con ?formato=pdf).
    """
    permission_classes = [permissions.IsAdminUser]

    def get_financial_data(self, request):
        # Esta función extrae la lógica de cálculo para poder reutilizarla
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

        if formato == 'pdf':
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="reporte_financiero_{data["rango_fechas"]["inicio"]}_a_{data["rango_fechas"]["fin"]}.pdf"'
            
            # Llamamos a la función que genera el PDF
            return generar_reporte_financiero_pdf(response, data)
        
        # Por defecto, devolvemos JSON
        return Response(data, status=status.HTTP_200_OK)
    


class ReporteUsoAreasComunesView(APIView):
    """
    Genera un reporte con estadísticas de uso de las áreas comunes
    dentro de un rango de fechas.
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        # 1. Obtener el rango de fechas de los query params
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

        # 2. Realizar la consulta y agregación de datos
        # Filtramos las reservas pagadas dentro del rango de fechas
        reservas_en_rango = Reserva.objects.filter(
            fecha_reserva__range=[fecha_inicio, fecha_fin],
            pagada=True
        )

        # Calculamos la duración de cada reserva en horas
        duracion_horas = ExpressionWrapper(
            (F('hora_fin') - F('hora_inicio')),
            output_field=fields.DurationField()
        )

        # Agrupamos por área común y calculamos las estadísticas
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

        # 3. Formatear la respuesta para que sea más legible
        reporte_data = []
        for item in estadisticas:
            # La duración viene como un objeto timedelta, lo convertimos a horas
            total_segundos = item['total_horas_reservadas'].total_seconds() if item['total_horas_reservadas'] else 0
            horas = round(total_segundos / 3600, 2)

            reporte_data.append({
                "area_comun": item['nombre_area'],
                "cantidad_reservas": item['cantidad_reservas'],
                "total_horas_reservadas": horas,
                "ingresos_generados": item['ingresos_generados'] or 0
            })

        # 4. Construir la respuesta final
        data = {
            'rango_fechas': {
                'inicio': fecha_inicio.isoformat(),
                'fin': fecha_fin.isoformat(),
            },
            'reporte': reporte_data
        }

        return Response(data, status=status.HTTP_200_OK)