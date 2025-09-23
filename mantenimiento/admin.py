from django.contrib import admin
from .models import PersonalMantenimiento, SolicitudMantenimiento

admin.site.register(PersonalMantenimiento)
@admin.register(SolicitudMantenimiento)
class SolicitudMantenimientoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'propiedad', 'estado', 'asignado_a', 'fecha_creacion')
    list_filter = ('estado', 'asignado_a')
    search_fields = ('titulo', 'descripcion')
    list_editable = ('estado', 'asignado_a')