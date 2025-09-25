from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Importamos únicamente el ViewSet que estamos usando
from .views import SolicitudMantenimientoViewSet

router = DefaultRouter()

# Registramos únicamente la ruta para las solicitudes de mantenimiento
router.register(r'solicitudes', SolicitudMantenimientoViewSet, basename='solicitudmantenimiento')

urlpatterns = [
    path('', include(router.urls)),
]