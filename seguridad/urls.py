from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import VisitanteViewSet, VisitaViewSet, VehiculoViewSet, ControlAccesoVehicularView

router = DefaultRouter()
router.register(r'visitantes', VisitanteViewSet)
router.register(r'visitas', VisitaViewSet, basename='visita')
router.register(r'vehiculos', VehiculoViewSet)

urlpatterns = [
    path('accesos/verificar-placa/', ControlAccesoVehicularView.as_view(), name='verificar_placa'),
] + router.urls 