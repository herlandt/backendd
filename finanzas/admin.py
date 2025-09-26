from django.contrib import admin
from .models import Gasto, Pago, Multa, PagoMulta, Reserva


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ('id', 'propiedad', 'monto', 'mes', 'anio', 'pagado')
    list_filter = ('anio', 'mes', 'pagado')
    search_fields = ('propiedad__numero_casa', 'descripcion')


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'gasto', 'usuario', 'monto_pagado', 'fecha_pago')
    list_filter = ('fecha_pago',)
    search_fields = ('gasto__propiedad__numero_casa', 'usuario__username')


@admin.register(Multa)
class MultaAdmin(admin.ModelAdmin):
    list_display = ('id', 'propiedad', 'concepto', 'monto', 'mes', 'anio', 'pagado')
    list_filter = ('anio', 'mes', 'pagado')
    search_fields = ('propiedad__numero_casa', 'concepto', 'descripcion')


@admin.register(PagoMulta)
class PagoMultaAdmin(admin.ModelAdmin):
    list_display = ('id', 'multa', 'usuario', 'monto_pagado', 'fecha_pago')
    list_filter = ('fecha_pago',)
    search_fields = ('multa__propiedad__numero_casa', 'usuario__username')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'area_comun', 'usuario', 'fecha_reserva', 'hora_inicio', 'hora_fin', 'costo_total', 'pagada')
    list_filter = ('fecha_reserva', 'pagada')
    search_fields = ('area_comun__nombre', 'usuario__username')
