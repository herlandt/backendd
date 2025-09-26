from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PersonalMantenimientoViewSet, SolicitudMantenimientoViewSet

router = DefaultRouter()
router.register(r"personal", PersonalMantenimientoViewSet, basename="personal-mantenimiento")
router.register(r"solicitudes", SolicitudMantenimientoViewSet, basename="solicitud-mantenimiento")

urlpatterns = [
    path("", include(router.urls)),
]
