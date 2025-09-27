from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "seguridad"

router = DefaultRouter()
router.register(r"visitantes", views.VisitanteViewSet, basename="visitante")
router.register(r"vehiculos", views.VehiculoViewSet, basename="vehiculo")
router.register(r"visitas", views.VisitaViewSet, basename="visita")

urlpatterns = [
    path("control-acceso-vehicular/", views.control_acceso_vehicular, name="control-acceso-vehicular"),
    path("control-salida-vehicular/", views.control_salida_vehicular, name="control-salida-vehicular"),
    path("", include(router.urls)),
    path("visitas-abiertas/", views.visitas_abiertas, name="visitas-abiertas"),
]
