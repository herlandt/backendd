# seguridad/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VisitanteViewSet,
    VisitaViewSet,
    VehiculoViewSet,
    ControlAccesoVehicularView,
)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'visitantes', VisitanteViewSet)
router.register(r'visitas', VisitaViewSet)
router.register(r'vehiculos', VehiculoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('control-acceso-vehicular/', views.ControlAccesoVehicularView.as_view()),
    path('control-acceso-vehicular/salida/', views.RegistrarSalidaVehicularView.as_view()),
]