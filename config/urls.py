# backend/config/urls.py (CORREGIDO)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.shortcuts import redirect

from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from usuarios.views import RegistroView, RegistrarDispositivoView
from rest_framework.authtoken.views import obtain_auth_token
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from .api_views import APIWelcomeView

def redirect_to_api(request):
    """Redirecciona la URL raíz a la vista de bienvenida de la API"""
    return redirect('/api/')

urlpatterns = [
    # Redirección desde la raíz a la API
    path('', redirect_to_api, name='root_redirect'),
    
    path('admin/', admin.site.urls),

    # Vista de bienvenida de la API
    path('api/', APIWelcomeView.as_view(), name='api_welcome'),

    # Autenticación y registro de usuarios (se quedan en la raíz de la API)
    path('api/login/', obtain_auth_token, name='api_token_auth'),
    path('api/registro/', RegistroView.as_view(), name='api_registro'),
    path('api/dispositivos/registrar/', RegistrarDispositivoView.as_view(), name='registrar_dispositivo'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Endpoints de cada app con su propio prefijo
    path('api/usuarios/', include('usuarios.urls')),
    path('api/condominio/', include('condominio.urls')),
    path('api/finanzas/', include('finanzas.urls')),
    path("api/seguridad/", include(("seguridad.urls", "seguridad"), namespace="seguridad")),
    path('api/mantenimiento/', include('mantenimiento.urls')), # <-- AHORA TIENE SU PREFIJO
    path('api/auditoria/', include('auditoria.urls')), # <-- NUEVO: URLs de auditoría

    # URLs para la API navegable
    path('api-auth/', include('rest_framework.urls')),
    path("api/notificaciones/", include(("notificaciones.urls", "notificaciones"), namespace="notificaciones")),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)