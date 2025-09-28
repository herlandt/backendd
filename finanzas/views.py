from datetime import datetime
from decimal import Decimal
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Gasto, Pago, Multa, PagoMulta, Reserva
from .serializers import (
    GastoSerializer, PagoSerializer,
    MultaSerializer, PagoMultaSerializer,
    ReservaSerializer
)
from condominio.models import Propiedad


# =========================
#        GASTOS
# =========================
class GastoViewSet(viewsets.ModelViewSet):
    queryset = Gasto.objects.select_related('propiedad').all()
    serializer_class = GastoSerializer

    @action(detail=False, methods=['post'], url_path='crear_mensual')
    def crear_mensual(self, request):
        descripcion = (request.data.get('descripcion') or '').strip()
        monto_raw = request.data.get('monto')
        fecha_str = request.data.get('fecha') or request.data.get('fecha_emision')
        venc_str = request.data.get('fecha_vencimiento')

        # monto
        if not monto_raw:
            return Response({'detail': 'monto es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            monto = float(monto_raw)
            if monto <= 0:
                return Response({'detail': 'monto debe ser > 0.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'detail': 'monto inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        # fecha emisión (para definir mes/anio)
        if fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({'detail': 'fecha inválida. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            fecha = timezone.now().date()

        # fecha vencimiento (opcional)
        fecha_vencimiento = None
        if venc_str:
            try:
                fecha_vencimiento = datetime.strptime(venc_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({'detail': 'fecha_vencimiento inválida. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        mes = fecha.month
        anio = fecha.year

        creados = 0
        duplicados = []
        errores = []

        for prop in Propiedad.objects.all():
            try:
                Gasto.objects.create(
                    propiedad=prop,
                    monto=monto,
                    fecha_emision=fecha,
                    fecha_vencimiento=fecha_vencimiento,
                    descripcion=descripcion,
                    pagado=False,
                    mes=mes,
                    anio=anio,
                )
                creados += 1
            except IntegrityError:
                duplicados.append(prop.id)
            except Exception as e:
                errores.append({'propiedad_id': prop.id, 'error': str(e)})

        payload = {
            'status': f'Gastos creados: {creados}',
            'mes': mes,
            'anio': anio,
            'duplicados': duplicados,
            'errores': errores
        }
        http_status = status.HTTP_201_CREATED if creados else status.HTTP_200_OK
        return Response(payload, status=http_status)

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
        """
        Body: {"ids":[1,2,3]}  -> paga todas las NO pagadas en la lista.
        """
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
        """
        Body: {"ids":[1,2,3]}
        """
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

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class PagoMultaViewSet(viewsets.ModelViewSet):
    queryset = PagoMulta.objects.select_related('multa', 'usuario').all()
    serializer_class = PagoMultaSerializer

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


# =========================
#        RESERVAS
# =========================
class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.select_related('area_comun', 'usuario').all()
    serializer_class = ReservaSerializer

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


# --- imports estándar que ya usas arriba ---
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# NUEVOS imports
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
import io
import csv

# Importamos modelos sólo si existen para no romper en entornos vacíos
try:
    from .models import Pago, PagoMulta
except Exception:
    Pago = None
    PagoMulta = None


# ------------ Comprobantes (PDF/TXT fallback) ------------

class _ReciboBase:
    """Helper para generar PDF si reportlab está instalado; si no, devolvemos TXT."""
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
    permission_classes = [AllowAny]  # Para probar fácil en navegador

    def get(self, request, pago_id: int, *args, **kwargs):
        title = f"Recibo de pago #{pago_id}"
        lines = []

        if Pago is not None:
            try:
                p = Pago.objects.get(pk=pago_id)
                monto = getattr(p, "monto", None) or getattr(p, "monto_total", None) or getattr(p, "importe", None)
                fecha = getattr(p, "fecha_pago", None) or getattr(p, "fecha", None)
                lines += [f"Monto: {monto}", f"Fecha: {fecha}"]
            except Pago.DoesNotExist:
                lines.append("Pago no encontrado (recibo de demostración).")

        pdf = _ReciboBase.build_pdf(title, lines)
        if pdf:
            resp = HttpResponse(pdf, content_type="application/pdf")
            resp["Content-Disposition"] = f'attachment; filename="recibo_pago_{pago_id}.pdf"'
            return resp

        # Fallback TXT si no hay reportlab
        resp = HttpResponse(f"{title}\n" + "\n".join(lines), content_type="text/plain; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="recibo_pago_{pago_id}.txt"'
        return resp


class ReciboPagoMultaPDFView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pago_multa_id: int, *args, **kwargs):
        title = f"Recibo de pago de multa #{pago_multa_id}"
        lines = []

        if PagoMulta is not None:
            try:
                pm = PagoMulta.objects.get(pk=pago_multa_id)
                monto = getattr(pm, "monto", None) or getattr(pm, "monto_total", None) or getattr(pm, "importe", None)
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


# ------------ Reportes (stub funcional para probar URLs) ------------

class ReporteMorosidadView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Devuelve CSV o JSON vacío (plantilla) para probar la ruta.
        Params: ?mes=9&anio=2025&fmt=csv
        """
        mes = request.query_params.get("mes")
        anio = request.query_params.get("anio")
        fmt = (request.query_params.get("fmt") or "json").lower()

        # Aquí más adelante añadimos el cálculo real.
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
        """
        Devuelve un resumen simple para probar la ruta.
        Params: ?desde=YYYY-MM-DD&hasta=YYYY-MM-DD
        """
        desde = request.query_params.get("desde")
        hasta = request.query_params.get("hasta")
        # Plantilla: luego calculamos ingresos/egresos reales.
        return Response({"desde": desde, "hasta": hasta, "ingresos": 0, "egresos": 0})


# ... (importaciones existentes)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .services import iniciar_pago_qr
from .models import Pago

class IniciarPagoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pago_id, *args, **kwargs):
        """
        Endpoint para que la app móvil solicite el QR de un pago pendiente.
        """
        resultado = iniciar_pago_qr(pago_id)
        if "error" in resultado:
            return Response(resultado, status=status.HTTP_400_BAD_REQUEST)
        return Response(resultado, status=status.HTTP_200_OK)

class WebhookConfirmacionPagoView(APIView):
    permission_classes = [AllowAny] # Debe ser público para que la pasarela pueda llamarlo

    def post(self, request, *args, **kwargs):
        """
        Endpoint que PagosNet llamará cuando un pago se complete.
        """
        data = request.data
        pago_id_externo = data.get('idExterno')
        estado_transaccion = data.get('estado')

        try:
            pago = Pago.objects.get(id=int(pago_id_externo))
            if estado_transaccion == 'PAGADO':
                pago.estado_pago = 'PAGADO'
                pago.save()
                # Aquí podrías enviar una notificación push al usuario
                print(f"Pago {pago.id} confirmado con éxito!")
            else:
                pago.estado_pago = 'FALLIDO'
                pago.save()
        except Pago.DoesNotExist:
            # La pasarela envió un ID que no conocemos, lo ignoramos o lo registramos
            pass
        
        return Response(status=status.HTTP_200_OK)
    
from .models import Reserva

class PagarReservaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, reserva_id, *args, **kwargs):
        try:
            reserva = Reserva.objects.get(id=reserva_id, usuario=request.user)
            if reserva.pagada:
                return Response({"detail": "Esta reserva ya fue pagada."}, status=status.HTTP_400_BAD_REQUEST)

            # Creamos un objeto Pago para la reserva
            pago = Pago.objects.create(
                reserva=reserva,
                usuario=request.user,
                monto_pagado=reserva.costo_total,
                estado_pago='PENDIENTE'
            )

            # Reutilizamos el servicio de QR que ya tienes
            resultado = iniciar_pago_qr(pago.id)
            if "error" in resultado:
                return Response(resultado, status=status.HTTP_400_BAD_REQUEST)
            return Response(resultado, status=status.HTTP_200_OK)

        except Reserva.DoesNotExist:
            return Response({"detail": "Reserva no encontrada."}, status=status.HTTP_404_NOT_FOUND)
        

# V AÑADE ESTA NUEVA CLASE AL FINAL V
class PagarReservaView(APIView):
    def post(self, request, reserva_id):
        # Aquí irá tu lógica para procesar el pago de la reserva.
        # Por ejemplo, encontrar la reserva, crear un objeto de Pago, etc.
        return Response(
            {"message": f"Lógica de pago para la reserva {reserva_id} aún no implementada."}, 
            status=status.HTTP_200_OK
        )