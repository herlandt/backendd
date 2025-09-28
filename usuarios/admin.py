# En usuarios/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Residente

# Define el Residente para que aparezca dentro del User
class ResidenteInline(admin.StackedInline):
    model = Residente
    can_delete = False
    verbose_name_plural = 'Perfil de Residente'

# Extiende el admin de User para incluir el perfil de Residente
class UserAdmin(BaseUserAdmin):
    inlines = (ResidenteInline,)

# Vuelve a registrar el admin de User con la nueva configuración mejorada
admin.site.unregister(User)
admin.site.register(User, UserAdmin)