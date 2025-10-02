# condominio/urls.py (Corregido)
from rest_framework.routers import DefaultRouter
# --- CORRECCIÓN AQUÍ ---
# Se añade ReglaViewSet a la lista de importaciones desde las vistas.
from .views import PropiedadViewSet, AreaComunViewSet, AvisoViewSet, ReglaViewSet, LecturaAvisoViewSet

router = DefaultRouter()
router.register(r'propiedades', PropiedadViewSet)
router.register(r'areas-comunes', AreaComunViewSet)
router.register(r'avisos', AvisoViewSet)
router.register(r'lecturas-avisos', LecturaAvisoViewSet, basename='lectura-aviso')
# Esta línea ahora funcionará porque ReglaViewSet está importado.
router.register(r'reglas', ReglaViewSet, basename='regla')

urlpatterns = router.urls