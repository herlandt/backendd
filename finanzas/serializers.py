from rest_framework import serializers
from .models import Gasto, Pago, Multa, PagoMulta, Reserva
from condominio.models import Propiedad, AreaComun


class PropiedadTinySerializer(serializers.ModelSerializer):
    class Meta:
        model = Propiedad
        fields = ('id', 'numero_casa',)


class AreaComunTinySerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaComun
        fields = ('id', 'nombre',)


# ----- GASTOS -----
class GastoSerializer(serializers.ModelSerializer):
    propiedad = PropiedadTinySerializer(read_only=True)
    propiedad_id = serializers.PrimaryKeyRelatedField(
        source='propiedad', queryset=Propiedad.objects.all(), write_only=True
    )

    class Meta:
        model = Gasto
        fields = (
            'id', 'propiedad', 'propiedad_id', 'monto',
            'fecha_emision', 'fecha_vencimiento',
            'descripcion', 'pagado', 'mes', 'anio'
        )
        read_only_fields = ('mes', 'anio', 'pagado')


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = ('id', 'gasto', 'usuario', 'monto_pagado', 'fecha_pago', 'comprobante')
        read_only_fields = ('usuario', 'fecha_pago')


# ----- MULTAS -----
class MultaSerializer(serializers.ModelSerializer):
    propiedad = PropiedadTinySerializer(read_only=True)
    propiedad_id = serializers.PrimaryKeyRelatedField(
        source='propiedad', queryset=Propiedad.objects.all(), write_only=True
    )

    class Meta:
        model = Multa
        fields = (
            'id', 'propiedad', 'propiedad_id', 'concepto', 'monto',
            'fecha_emision', 'fecha_vencimiento',
            'descripcion', 'pagado', 'mes', 'anio'
        )
        read_only_fields = ('mes', 'anio', 'pagado')


class PagoMultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagoMulta
        fields = ('id', 'multa', 'usuario', 'monto_pagado', 'fecha_pago', 'comprobante')
        read_only_fields = ('usuario', 'fecha_pago')


# ----- RESERVAS -----
class ReservaSerializer(serializers.ModelSerializer):
    area_comun = AreaComunTinySerializer(read_only=True)
    area_comun_id = serializers.PrimaryKeyRelatedField(
        source='area_comun', queryset=AreaComun.objects.all(), write_only=True
    )

    class Meta:
        model = Reserva
        fields = (
            'id', 'area_comun', 'area_comun_id', 'usuario',
            'fecha_reserva', 'hora_inicio', 'hora_fin',
            'costo_total', 'pagada'
        )
        read_only_fields = ('usuario',)
