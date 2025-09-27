from django.contrib import admin
from .models import Visitante, Vehiculo, Visita


@admin.register(Visitante)
class VisitanteAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre_completo", "documento", "telefono", "email")
    search_fields = ("nombre_completo", "documento", "telefono", "email")
    # No uses 'documento_identidad' en ninguna parte.


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ("placa", "visitante", "propiedad", "es_residente_bool")
    list_filter = ("propiedad",)
    search_fields = (
        "placa",
        "visitante__nombre_completo",
        "visitante__documento",
        "propiedad__numero_casa",
    )
    # Evita E040 sin depender de search_fields de otros ModelAdmin:
    raw_id_fields = ("visitante", "propiedad")

    def es_residente_bool(self, obj):
        return obj.es_residente
    es_residente_bool.boolean = True
    es_residente_bool.short_description = "¿Residente?"


@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = (
        "visitante",
        "propiedad",
        "fecha_ingreso_programado",
        "fecha_salida_programada",
        "ingreso_real",
        "salida_real",
    )
    list_filter = ("propiedad",)
    search_fields = (
        "visitante__nombre_completo",
        "visitante__documento",
        "propiedad__numero_casa",
    )
    raw_id_fields = ("visitante", "propiedad")
    # No referenciar 'registrado_por' porque ya no existe.
