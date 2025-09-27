from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PropiedadViewSet, AreaComunViewSet, AvisoViewSet # Verifica esta línea

router = DefaultRouter()
router.register(r'propiedades', PropiedadViewSet)
router.register(r'areas-comunes', AreaComunViewSet)
router.register(r'avisos', AvisoViewSet) # Y esta línea
router.register(r'reglas', ReglaViewSet, basename='regla')
urlpatterns = [
    path('', include(router.urls)),
]