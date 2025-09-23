from rest_framework.routers import DefaultRouter
from .views import PropiedadViewSet, AreaComunViewSet

router = DefaultRouter()
router.register(r'propiedades', PropiedadViewSet)
router.register(r'areas-comunes', AreaComunViewSet)

urlpatterns = router.urls