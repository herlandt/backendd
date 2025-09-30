# En usuarios/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Residente, UserProfile

# Define el Residente para que aparezca dentro del User
class ResidenteInline(admin.StackedInline):
    model = Residente
    can_delete = False
    verbose_name_plural = 'Perfil de Residente'

# Define el UserProfile para que aparezca dentro del User
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil de Usuario'

# Extiende el admin de User para incluir el perfil de Residente y UserProfile
class UserAdmin(BaseUserAdmin):
    inlines = (ResidenteInline, UserProfileInline,)

# Vuelve a registrar el admin de User con la nueva configuración mejorada
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Registra UserProfile separadamente también
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email']