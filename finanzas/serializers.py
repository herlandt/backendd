from rest_framework import serializers
from .models import Gasto, Pago, Reserva

class GastoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gasto
        fields = ['id', 'monto', 'fecha_emision', 'fecha_vencimiento', 'descripcion', 'pagado']

class PagoSerializer(serializers.ModelSerializer):
    usuario = serializers.ReadOnlyField(source='usuario.username')
    class Meta:
        model = Pago
        fields = ['id', 'gasto', 'usuario', 'monto_pagado', 'fecha_pago', 'comprobante']

class ReservaSerializer(serializers.ModelSerializer):
    usuario = serializers.ReadOnlyField(source='usuario.username')
    area_comun_nombre = serializers.CharField(source='area_comun.nombre', read_only=True)
    class Meta:
        model = Reserva
        fields = ['id', 'area_comun', 'area_comun_nombre', 'usuario', 'fecha_reserva', 'hora_inicio', 'hora_fin', 'costo_total', 'pagada']
        extra_kwargs = {
            'area_comun': {'write_only': True},
            'costo_total': {'read_only': True},
            'pagada': {'read_only': True},
        }