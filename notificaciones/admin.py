from django.contrib import admin
from .models import DeviceToken, Dispositivo

@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "platform", "token", "active", "created_at")
    search_fields = ("token", "user__username", "user__email")
    list_filter = ("platform", "active")

@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "token_dispositivo", "activo", "fecha_creacion")
    search_fields = ("token_dispositivo", "usuario__username", "usuario__email")
    list_filter = ("activo",)
