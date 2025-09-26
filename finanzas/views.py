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
