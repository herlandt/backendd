from decimal import Decimal
from django.db.models import Sum
from rest_framework import serializers
from .models import Gasto, Pago, Reserva
from condominio.serializers import PropiedadSerializer


class GastoSerializer(serializers.ModelSerializer):
    # Leer: detalle de propiedad
    propiedad = PropiedadSerializer(read_only=True)
    # Escribir: id simple
    propiedad_id = serializers.IntegerField(write_only=True)

    # Campos calculados
    total_pagado = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    saldo = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Gasto
        fields = [
            'id', 'propiedad', 'propiedad_id', 'monto',
            'fecha_emision', 'fecha_vencimiento', 'descripcion', 'pagado',
            'mes', 'anio', 'total_pagado', 'saldo'
        ]

    def create(self, validated_data):
        # Usamos propiedad_id para setear la FK
        propiedad_id = validated_data.pop('propiedad_id')
        return Gasto.objects.create(propiedad_id=propiedad_id, **validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['total_pagado'] = str(instance.total_pagado)
        data['saldo'] = str(instance.saldo)
        return data


class PagoSerializer(serializers.ModelSerializer):
    usuario = serializers.ReadOnlyField(source='usuario.username')

    class Meta:
        model = Pago
        fields = ['id', 'gasto', 'usuario', 'monto_pagado', 'fecha_pago', 'comprobante']

    def validate(self, attrs):
        gasto = attrs['gasto']
        monto = attrs['monto_pagado'] or Decimal('0')

        if monto <= 0:
            raise serializers.ValidationError("El monto del pago debe ser mayor a 0.")

        pagado_hasta_hoy = gasto.pagos.aggregate(s=Sum('monto_pagado'))['s'] or Decimal('0')
        restante = (gasto.monto or Decimal('0')) - pagado_hasta_hoy

        if monto > restante:
            raise serializers.ValidationError(f"El monto excede el saldo del gasto ({restante}).")

        return attrs


class ReservaSerializer(serializers.ModelSerializer):
    usuario = serializers.ReadOnlyField(source='usuario.username')
    area_comun_nombre = serializers.CharField(source='area_comun.nombre', read_only=True)

    class Meta:
        model = Reserva
        fields = ['id', 'area_comun', 'area_comun_nombre', 'usuario',
                  'fecha_reserva', 'hora_inicio', 'hora_fin', 'costo_total', 'pagada']
        extra_kwargs = {
            'area_comun': {'write_only': True},
            'costo_total': {'read_only': True},
            'pagada': {'read_only': True},
        }
