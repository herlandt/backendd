# Fichero: finanzas/views.py

from datetime import date
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from .models import Gasto, Pago, Reserva
from .serializers import GastoSerializer, PagoSerializer, ReservaSerializer
from usuarios.models import Residente
from condominio.models import Propiedad

class GastoViewSet(viewsets.ModelViewSet):
    serializer_class = GastoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        # SOLUCIÓN: Si el usuario es administrador (staff), devuelve todos los gastos.
        if user.is_staff:
            return Gasto.objects.all().order_by('-fecha_vencimiento')
        
        # Si no, se ejecuta la lógica original para residentes.
        try:
            propiedades_usuario = Residente.objects.filter(usuario=user).values_list('propiedad', flat=True)
            return Gasto.objects.filter(propiedad__in=propiedades_usuario).order_by('-fecha_vencimiento')
        except Residente.DoesNotExist:
            return Gasto.objects.none()

    @action(detail=True, methods=['post'])
    def pagar(self, request, pk=None):
        gasto = self.get_object()
        if gasto.pagado:
            return Response({'status': 'este gasto ya fue pagado'}, status=status.HTTP_400_BAD_REQUEST)
        gasto.pagado = True
        gasto.save()
        Pago.objects.create(
            gasto=gasto, usuario=request.user, monto_pagado=gasto.monto,
            comprobante=f"SIMULADO-{gasto.id}-{request.user.id}"
        )
        return Response({'status': 'pago registrado con éxito'})

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def crear_mensual(self, request):
        # ... (esta lógica ya es correcta) ...
        descripcion = request.data.get('descripcion')
        monto = request.data.get('monto')
        fecha_vencimiento_str = request.data.get('fecha_vencimiento')
        if not all([descripcion, monto, fecha_vencimiento_str]):
            return Response({'error': 'Faltan datos'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            fecha_vencimiento = date.fromisoformat(fecha_vencimiento_str)
        except ValueError:
            return Response({'error': 'Formato de fecha debe ser AAAA-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
        propiedades = Propiedad.objects.all()
        for propiedad in propiedades:
            Gasto.objects.create(
                propiedad=propiedad, monto=monto, fecha_vencimiento=fecha_vencimiento,
                descripcion=descripcion, pagado=False
            )
        return Response({'status': f'Se crearon {propiedades.count()} gastos con éxito'}, status=status.HTTP_201_CREATED)

class PagoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PagoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # SOLUCIÓN: Si es admin, ve todos los pagos.
        if user.is_staff:
            return Pago.objects.all().order_by('-fecha_pago')
        return Pago.objects.filter(usuario=user).order_by('-fecha_pago')

class ReservaViewSet(viewsets.ModelViewSet):
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # SOLUCIÓN: Si es admin, ve todas las reservas.
        if user.is_staff:
            return Reserva.objects.all().order_by('-fecha_reserva')
        return Reserva.objects.filter(usuario=user).order_by('-fecha_reserva')

    def perform_create(self, serializer):
        # ... (esta lógica ya es correcta) ...
        area_comun = serializer.validated_data['area_comun']
        fecha_reserva = serializer.validated_data['fecha_reserva']
        hora_inicio = serializer.validated_data['hora_inicio']
        hora_fin = serializer.validated_data['hora_fin']
        if area_comun.horario_apertura and (hora_inicio < area_comun.horario_apertura or hora_fin > area_comun.horario_cierre):
            raise ValidationError(f"El horario debe estar entre {area_comun.horario_apertura} y {area_comun.horario_cierre}.")
        
        conflictos = Reserva.objects.filter(
            area_comun=area_comun,
            fecha_reserva=fecha_reserva,
        ).filter(
            Q(hora_inicio__lt=hora_fin) & Q(hora_fin__gt=hora_inicio)
        )
        
        if conflictos.exists():
            raise ValidationError("Ya existe una reserva en este horario. Por favor, elige otra hora.")
        
        costo = area_comun.costo_reserva
        serializer.save(
            usuario=self.request.user,
            costo_total=costo,
            pagada=(costo == 0.00)
        )