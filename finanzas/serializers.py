# Fichero: finanzas/serializers.py

from rest_framework import serializers
from .models import Gasto, Pago, Reserva
from condominio.serializers import PropiedadSerializer # Importamos para mostrar el detalle al leer

class GastoSerializer(serializers.ModelSerializer):
    # Para LEER: Muestra los detalles completos de la propiedad, no solo el ID.
    propiedad = PropiedadSerializer(read_only=True)
    # Para ESCRIBIR: Acepta un simple ID para la propiedad.
    propiedad_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Gasto
        # Añadimos 'propiedad' (para lectura) y 'propiedad_id' (para escritura)
        fields = ['id', 'propiedad', 'propiedad_id', 'monto', 'fecha_emision', 'fecha_vencimiento', 'descripcion', 'pagado']

    def create(self, validated_data):
        # Usamos 'propiedad_id' para crear la relación con la propiedad correcta
        return Gasto.objects.create(**validated_data)

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