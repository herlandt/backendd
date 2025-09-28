# En usuarios/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Usuario, Residente

# --- PASO 1: Eliminar el registro del User antiguo de Django ---
# Esto asegura que solo tu modelo 'Usuario' aparezca en el admin.
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

# --- PASO 2: Configurar el perfil 'Residente' para que aparezca DENTRO de 'Usuario' ---
class ResidenteInline(admin.StackedInline):
    model = Residente
    can_delete = False
    verbose_name_plural = 'Perfil de Residente'
    fk_name = 'usuario'

# --- PASO 3: Crear una vista de admin personalizada para tu 'Usuario' ---
class CustomUserAdmin(UserAdmin):
    inlines = (ResidenteInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

# --- PASO 4: Registrar tu modelo 'Usuario' con la nueva configuración ---
# Esto reemplaza el admin de User por el tuyo.
admin.site.register(Usuario, CustomUserAdmin)

# NOTA: No registramos 'Residente' por separado para evitar duplicados.
# admin.site.register(Residente) <-- Esta línea NO debe existir.