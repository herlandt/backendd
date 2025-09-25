from rest_framework import permissions
# No importamos nada de usuarios.models aquí

class IsMantenimientoOrAdminUser(permissions.BasePermission):
    """
    Permiso para permitir solo al personal de mantenimiento o administradores
    modificar objetos.
    """
    def has_object_permission(self, request, view, obj):
        # Permisos de lectura para todos
        if request.method in permissions.SAFE_METHODS:
            return True

        # Permisos de escritura solo para personal de mantenimiento o superusuarios
        user = request.user
        return hasattr(user, 'perfil_mantenimiento') or user.is_staff