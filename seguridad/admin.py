from django.contrib import admin
from .models import Visitante, Visita, Vehiculo


@admin.register(Visitante)
class VisitanteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_completo', 'documento_identidad')
    search_fields = ('nombre_completo', 'documento_identidad')


@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'propiedad', 'visitante',
        'fecha_ingreso_programado', 'fecha_salida_programada',
        'ingreso_real', 'salida_real', 'registrado_por'
    )
    list_filter = ('propiedad',)
    search_fields = (
        'visitante__nombre_completo',
        'visitante__documento_identidad',
        'propiedad__numero_casa',
        'registrado_por__username',
    )
    # Evita dependencias con otros admin (no dispara admin.E040)
    raw_id_fields = ('propiedad', 'visitante', 'registrado_por')


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('id', 'placa', 'marca', 'modelo', 'propiedad', 'visitante')
    search_fields = (
        'placa', 'marca', 'modelo',
        'visitante__nombre_completo', 'propiedad__numero_casa'
    )
    raw_id_fields = ('propiedad', 'visitante')
