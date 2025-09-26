from django.contrib import admin, messages
from .models import Gasto, Pago, Reserva


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ('id', 'propiedad', 'monto', 'mes', 'anio', 'pagado')
    list_filter = ('pagado', 'mes', 'anio', 'propiedad')
    search_fields = ('propiedad__numero_casa', 'descripcion')
    actions = ['registrar_pago_completo']

    @admin.action(description='Registrar pago (completo) de los seleccionados')
    def registrar_pago_completo(self, request, queryset):
        hechos = 0
        ya = 0
        for g in queryset.select_related('propiedad'):
            if g.pagado:
                ya += 1
                continue
            Pago.objects.create(
                gasto=g,
                usuario=request.user if request.user.is_authenticated else None,
                monto_pagado=g.monto,
            )
            g.pagado = True
            g.save(update_fields=['pagado'])
            hechos += 1

        if hechos:
            self.message_user(request, f'{hechos} pagos registrados.', level=messages.SUCCESS)
        if ya:
            self.message_user(request, f'{ya} ya estaban pagados.', level=messages.WARNING)


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'gasto', 'monto_pagado', 'fecha_pago', 'usuario')
    list_filter = ('fecha_pago',)
    search_fields = ('gasto__propiedad__numero_casa',)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'area_comun', 'usuario', 'fecha_reserva', 'hora_inicio', 'hora_fin', 'pagada')
    list_filter = ('pagada', 'fecha_reserva')
