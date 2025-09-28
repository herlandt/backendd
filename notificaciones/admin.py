from django.contrib import admin
from .models import DeviceToken, Dispositivo

@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "platform", "token", "active", "created_at")
    list_filter  = ("platform", "active")
    search_fields= ("token", "user__username")

@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "token_dispositivo", "activo", "fecha_creacion")
    list_filter  = ("activo",)
    search_fields= ("token_dispositivo", "usuario__username")
