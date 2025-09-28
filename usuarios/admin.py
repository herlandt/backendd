# En usuarios/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Residente

# Define un "inline" para que Residente se edite dentro de Usuario
class ResidenteInline(admin.StackedInline):
    model = Residente
    can_delete = False
    verbose_name_plural = 'Perfil del Residente'
    fk_name = 'usuario'

# Define un nuevo admin para el modelo Usuario
class CustomUserAdmin(UserAdmin):
    inlines = (ResidenteInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

# Registra Usuario con la nueva configuración
admin.site.register(Usuario, CustomUserAdmin)

# ELIMINA LA SIGUIENTE LÍNEA QUE CAUSA EL DUPLICADO:
# admin.site.register(Residente)