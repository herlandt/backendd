# seguridad/admin.py
from django.contrib import admin
from .models import Visitante, Vehiculo, Visita  # <-- OJO: no importes Propiedad aquí

@admin.register(Visitante)
class VisitanteAdmin(admin.ModelAdmin):
    search_fields = ["nombre_completo", "documento_identidad"]
    list_display = ("nombre_completo", "documento_identidad", "telefono", "email")

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    search_fields = ["placa", "marca", "modelo", "visitante__nombre_completo", "propiedad__numero_casa"]
    list_display = ("placa", "marca", "modelo", "es_residente", "visitante", "propiedad")
    list_filter  = ("es_residente",)
    autocomplete_fields = ["visitante", "propiedad"]

@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    search_fields = ["visitante__nombre_completo", "propiedad__numero_casa", "motivo", "estado"]
    list_display = ("visitante", "propiedad", "fecha_ingreso_programado", "fecha_salida_programada", "estado")
    list_filter  = ("estado",)
    autocomplete_fields = ["visitante", "propiedad"]
