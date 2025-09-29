# auditoria/admin.py
from django.contrib import admin
from .models import Bitacora

@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    list_display = ("timestamp","usuario","ip_address","accion")
    list_filter = ("accion","timestamp")
    search_fields = ("usuario__username","accion","descripcion","ip_address")
    date_hierarchy = "timestamp"
