# backend/config/urls.py (CORREGIDO)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from usuarios.views import RegistroView, RegistrarDispositivoView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticación y registro de usuarios (se quedan en la raíz de la API)
    path('api/login/', obtain_auth_token, name='api_token_auth'),
    path('api/registro/', RegistroView.as_view(), name='api_registro'),
    path('api/dispositivos/registrar/', RegistrarDispositivoView.as_view(), name='registrar_dispositivo'),

    # Endpoints de cada app con su propio prefijo
    path('api/usuarios/', include('usuarios.urls')),
    path('api/condominio/', include('condominio.urls')),
    path('api/finanzas/', include('finanzas.urls')),
    path('api/seguridad/', include('seguridad.urls')),
    path('api/mantenimiento/', include('mantenimiento.urls')), # <-- AHORA TIENE SU PREFIJO

    # URLs para la API navegable
    path('api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)