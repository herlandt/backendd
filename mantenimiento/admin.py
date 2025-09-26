from django.contrib import admin
from .models import PersonalMantenimiento, SolicitudMantenimiento


@admin.register(PersonalMantenimiento)
class PersonalMantenimientoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "especialidad", "telefono", "activo")
    list_filter = ("activo", "especialidad")
    search_fields = ("nombre", "telefono", "especialidad")
    ordering = ("nombre",)


@admin.register(SolicitudMantenimiento)
class SolicitudMantenimientoAdmin(admin.ModelAdmin):
    # OJO: 'fecha_creacion' ahora sí existe en el modelo
    list_display = (
        "id",
        "propiedad",
        "solicitado_por",
        "titulo",
        "estado",
        "fecha_creacion",
        "asignado_a",
    )
    list_filter = ("estado", "fecha_creacion")
    search_fields = (
        "titulo",
        "descripcion",
        "propiedad__numero_casa",
        "solicitado_por__username",
        "asignado_a__nombre",
    )
    # Quitamos autocomplete_fields para no exigir search_fields
    # en admins externos (evita el error admin.E040).
    # autocomplete_fields = ("propiedad", "asignado_a", "solicitado_por")
    date_hierarchy = "fecha_creacion"
    ordering = ("-fecha_creacion",)
