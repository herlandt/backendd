# finanzas/admin.py
from django.contrib import admin
from .models import Gasto, Pago, Reserva

admin.site.register(Gasto)
admin.site.register(Pago)
admin.site.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('area_comun', 'usuario', 'fecha_reserva', 'hora_inicio', 'hora_fin', 'costo_total', 'pagada')
    list_filter = ('pagada', 'area_comun', 'fecha_reserva')
    search_fields = ('usuario__username', 'area_comun__nombre')
    list_editable = ('pagada',)