from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import (
    GastoViewSet, MultaViewSet,
    PagoViewSet, PagoMultaViewSet,
    ReservaViewSet,
)

router = DefaultRouter()
router.register(r'gastos', GastoViewSet, basename='gasto')
router.register(r'multas', MultaViewSet, basename='multa')
router.register(r'pagos', PagoViewSet, basename='pago')
router.register(r'pagos_multas', PagoMultaViewSet, basename='pago-multa')
router.register(r'reservas', ReservaViewSet, basename='reserva')

urlpatterns = [
    path('', include(router.urls)),
]
