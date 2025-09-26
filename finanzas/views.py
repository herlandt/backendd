from decimal import Decimal, InvalidOperation
from datetime import datetime, date
from django.db.models import Sum, Q
from django.utils import timezone
from django.db import IntegrityError, transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Gasto, Pago, Reserva
from .serializers import GastoSerializer, PagoSerializer, ReservaSerializer
from condominio.models import Propiedad


class GastoViewSet(viewsets.ModelViewSet):
    queryset = Gasto.objects.select_related('propiedad').all()
    serializer_class = GastoSerializer

    # -------- Filtros en /gastos/ --------
    def get_queryset(self):
        qs = super().get_queryset()

        p = self.request.query_params
        if p.get('propiedad_id'):
            qs = qs.filter(propiedad_id=p.get('propiedad_id'))
        if p.get('mes'):
            qs = qs.filter(mes=p.get('mes'))
        if p.get('anio'):
            qs = qs.filter(anio=p.get('anio'))
        if p.get('pagado') in ('true', 'false'):
            qs = qs.filter(pagado=(p.get('pagado') == 'true'))
        if p.get('vencido') == 'true':
            hoy = date.today()
            qs = qs.filter(pagado=False, fecha_vencimiento__lt=hoy)

        return qs.order_by('-anio', '-mes', 'propiedad_id')

    # -------- Crear gastos del mes para propiedades (todas u opcionales) --------
    @action(detail=False, methods=['post'], url_path='crear_mensual')
    def crear_mensual(self, request):
        descripcion = (request.data.get('descripcion') or '').strip()
        monto_raw = request.data.get('monto')
        fecha_str = request.data.get('fecha') or request.data.get('fecha_emision')
        venc_str = request.data.get('fecha_vencimiento')
        prop_ids = request.data.get('propiedad_ids')  # opcional: lista de IDs (si no, todos)

        # monto
        if not monto_raw:
            return Response({'detail': 'monto es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            monto = Decimal(str(monto_raw))
            if monto <= 0:
                return Response({'detail': 'monto debe ser > 0.'}, status=status.HTTP_400_BAD_REQUEST)
        except InvalidOperation:
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
                return Response({'detail': 'fecha_vencimiento inválida. Use YYYY-MM-DD.'},
                                status=status.HTTP_400_BAD_REQUEST)

        mes = fecha.month
        anio = fecha.year

        creados, duplicados, errores = 0, [], []

        props = Propiedad.objects.filter(id__in=prop_ids) if prop_ids else Propiedad.objects.all()
        for prop in props:
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

    # -------- Registrar pago (individual). Permite parcial con "monto" --------
    @action(detail=True, methods=['post'], url_path='registrar_pago')
    def registrar_pago(self, request, pk=None):
        gasto = self.get_object()
        # monto opcional. Si no viene, paga el total restante.
        raw = request.data.get('monto')
        restante = gasto.saldo

        if restante <= 0:
            return Response({'detail': 'El gasto no tiene saldo.'}, status=status.HTTP_400_BAD_REQUEST)

        if raw is None:
            monto = restante
        else:
            try:
                monto = Decimal(str(raw))
            except InvalidOperation:
                return Response({'detail': 'monto inválido.'}, status=status.HTTP_400_BAD_REQUEST)
            if monto <= 0 or monto > restante:
                return Response({'detail': f'El monto debe ser > 0 y <= saldo ({restante}).'},
                                status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            pago = Pago.objects.create(
                gasto=gasto,
                usuario=request.user if request.user.is_authenticated else None,
                monto_pagado=monto
            )
            # refrescamos saldo/pagado
            gasto.refresh_from_db()
            if gasto.saldo <= 0:
                gasto.pagado = True
                gasto.save(update_fields=['pagado'])

        return Response(PagoSerializer(pago).data, status=status.HTTP_201_CREATED)

    # -------- Registrar pagos masivos (paga el saldo de cada gasto) --------
    @action(detail=False, methods=['post'], url_path='registrar_pagos')
    def registrar_pagos(self, request):
        ids = request.data.get('gasto_ids') or []
        if not isinstance(ids, list) or not ids:
            return Response({'detail': 'gasto_ids debe ser una lista con IDs.'},
                            status=status.HTTP_400_BAD_REQUEST)

        creados, omitidos, errores = [], [], []
        for g in Gasto.objects.filter(id__in=ids):
            try:
                if g.saldo <= 0:
                    omitidos.append(g.id)
                    continue
                pago = Pago.objects.create(
                    gasto=g,
                    usuario=request.user if request.user.is_authenticated else None,
                    monto_pagado=g.saldo
                )
                g.refresh_from_db()
                if g.saldo <= 0 and not g.pagado:
                    g.pagado = True
                    g.save(update_fields=['pagado'])
                creados.append({'gasto_id': g.id, 'pago_id': pago.id})
            except Exception as e:
                errores.append({'gasto_id': g.id, 'error': str(e)})

        return Response({
            'pagos_creados': creados,
            'omitidos_sin_saldo': omitidos,
            'errores': errores
        }, status=status.HTTP_201_CREATED if creados else status.HTTP_200_OK)

    # -------- Deudas / pendientes --------
    @action(detail=False, methods=['get'], url_path='pendientes')
    def pendientes(self, request):
        qs = self.get_queryset().filter(pagado=False)
        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)

    # -------- Estado de cuenta --------
    @action(detail=False, methods=['get'], url_path='estado_cuenta')
    def estado_cuenta(self, request):
        propiedad_id = request.query_params.get('propiedad_id')
        if not propiedad_id:
            return Response({'detail': 'propiedad_id es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        qs = Gasto.objects.filter(propiedad_id=propiedad_id)
        if request.query_params.get('mes'):
            qs = qs.filter(mes=request.query_params.get('mes'))
        if request.query_params.get('anio'):
            qs = qs.filter(anio=request.query_params.get('anio'))

        total_gastos = qs.aggregate(s=Sum('monto'))['s'] or Decimal('0')
        total_pagado = Pago.objects.filter(gasto__in=qs).aggregate(s=Sum('monto_pagado'))['s'] or Decimal('0')
        saldo = total_gastos - total_pagado

        return Response({
            'propiedad_id': int(propiedad_id),
            'total_gastos': str(total_gastos),
            'total_pagado': str(total_pagado),
            'saldo': str(saldo),
        })


class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.select_related('gasto', 'usuario').all()
    serializer_class = PagoSerializer

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user if self.request.user.is_authenticated else None)


class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.select_related('area_comun', 'usuario').all()
    serializer_class = ReservaSerializer

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user if self.request.user.is_authenticated else None)
