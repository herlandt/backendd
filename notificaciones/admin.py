# notificaciones/admin.py

from django.contrib import admin
from .models import Dispositivo  # <-- Corregido para usar el nombre correcto

@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'token_dispositivo', 'fecha_creacion', 'activo')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('usuario__username', 'token_dispositivo')