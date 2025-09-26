from rest_framework.routers import DefaultRouter
from .views import GastoViewSet, PagoViewSet, ReservaViewSet

router = DefaultRouter()
router.register(r'gastos', GastoViewSet, basename='gasto')
router.register(r'pagos', PagoViewSet, basename='pago')
router.register(r'reservas', ReservaViewSet, basename='reserva')

urlpatterns = router.urls
