from django.contrib import admin
from django.utils import timezone
from .models import Gasto, Pago, Multa, PagoMulta, Reserva
from .models import Gasto, Pago, Multa, Reserva, Egreso, Ingreso

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
    list_display = ('id', 'propiedad', 'concepto', 'monto', 'pagado')
    list_filter = ('pagado', 'anio', 'mes')
    search_fields = ('propiedad__numero_casa', 'concepto', 'descripcion')

    def save_model(self, request, obj, form, change):
        """
        Si se marca la multa como 'pagada' en el admin, se crea automáticamente
        el registro de PagoMulta asociado a ella.
        """
        super().save_model(request, obj, form, change) # Guarda la multa primero

        # Si la multa está marcada como pagada Y todavía no tiene un pago asociado...
        if obj.pagado and not PagoMulta.objects.filter(multa=obj).exists():
            # ...creamos el pago.
            PagoMulta.objects.create(
                multa=obj,
                usuario=request.user, # Asigna el admin que está haciendo la operación
                monto_pagado=obj.monto,
                fecha_pago=timezone.now()
            )

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



@admin.register(Egreso)
class EgresoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'concepto', 'monto', 'categoria')
    list_filter = ('categoria', 'fecha')
    search_fields = ('concepto', 'descripcion')

@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'concepto', 'monto', 'pago_relacionado')
    list_filter = ('fecha',)
    search_fields = ('concepto', 'descripcion')

