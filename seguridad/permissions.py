# seguridad/permissions.py

from rest_framework.permissions import BasePermission
from django.conf import settings

class HasAPIKey(BasePermission):
    """
    Permite el acceso solo si la petición incluye la clave de API secreta correcta
    en la cabecera 'X-API-KEY'.
    """
    def has_permission(self, request, view):
        # Obtenemos la clave de la cabecera de la petición
        api_key_recibida = request.headers.get('X-API-KEY')
        
        # Obtenemos nuestra clave secreta desde la configuración de Django
        api_key_secreta = getattr(settings, 'CAMARA_API_KEY', None)

        # Si no hemos configurado una clave secreta en settings.py, denegamos por seguridad
        if not api_key_secreta:
            return False
            
        # Comparamos la clave recibida con nuestra clave secreta
        return api_key_recibida == api_key_secreta