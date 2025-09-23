from rest_framework.routers import DefaultRouter
from .views import PersonalMantenimientoViewSet, SolicitudMantenimientoViewSet

router = DefaultRouter()
router.register(r'personal', PersonalMantenimientoViewSet)
router.register(r'solicitudes', SolicitudMantenimientoViewSet, basename='solicitud_mantenimiento')

urlpatterns = router.urls