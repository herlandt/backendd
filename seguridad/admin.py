# seguridad/admin.py
from django.contrib import admin
from django.utils import timezone
from .models import Visitante, Vehiculo, Visita,EventoSeguridad 


# --- Acción: cerrar visitas vencidas (ingresó, no salió y ya venció la salida programada)
@admin.action(description="Cerrar visitas vencidas (salida = salida programada)")
def cerrar_visitas_vencidas(modeladmin, request, queryset):
    now = timezone.now()
    qs = queryset.filter(
        ingreso_real__isnull=False,
        salida_real__isnull=True,
        fecha_salida_programada__lt=now,
    )
    total = qs.count()
    for v in qs:
        v.salida_real = v.fecha_salida_programada
        v.save(update_fields=["salida_real"])
    modeladmin.message_user(request, f"Se cerraron {total} visitas vencidas.")


@admin.register(Visitante)
class VisitanteAdmin(admin.ModelAdmin):
    list_display = ("nombre_completo", "documento", "telefono", "email")
    search_fields = ("nombre_completo", "documento", "telefono", "email")
    list_per_page = 25


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ("placa", "propiedad", "visitante")
    search_fields = ("placa", "propiedad__numero_casa", "visitante__nombre_completo")
    list_filter = ("propiedad",)
    list_per_page = 25


@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = (
        "visitante", "propiedad",
        "fecha_ingreso_programado", "fecha_salida_programada",
        "ingreso_real", "salida_real", "estado",
    )
    search_fields = (
        "visitante__nombre_completo", "visitante__documento",
        "propiedad__numero_casa",
    )
    list_filter = ("propiedad",)
    date_hierarchy = "fecha_ingreso_programado"
    actions = [cerrar_visitas_vencidas]
    list_per_page = 25

    @admin.display(description="Estado")
    def estado(self, obj: Visita):
        if obj.ingreso_real and not obj.salida_real:
            return "ABIERTA"
        return "CERRADA"

from django.contrib import admin
from .models import Camera, Deteccion
admin.site.register(Camera)
admin.site.register(Deteccion)


@admin.register(EventoSeguridad)
class EventoSeguridadAdmin(admin.ModelAdmin):
    list_display = ('fecha_hora', 'placa_detectada', 'accion', 'tipo_evento', 'motivo')
    list_filter = ('accion', 'tipo_evento', 'fecha_hora')
    search_fields = ('placa_detectada', 'motivo')
    list_per_page = 25