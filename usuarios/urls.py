# backend/usuarios/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ResidenteViewSet, RegistroView, RegistrarDispositivoView, LoginView

router = DefaultRouter()
router.register("residentes", ResidenteViewSet, basename="residente")

urlpatterns = [
    # CRUD residentes (sólo admin)
    path("", include(router.urls)),

    # Auth
    path("login/", LoginView.as_view(), name="api_token_auth"),            # /api/usuarios/login/
    path("registro/", RegistroView.as_view(), name="api_registro"),        # /api/usuarios/registro/

    # Dispositivos
    path("dispositivos/registrar/", RegistrarDispositivoView.as_view(), name="registrar_dispositivo"),
]
