from django.urls import path
from .views import (
    RegistrarDeviceTokenView,
    EnviarNotificacionDemoView,
    RegistrarDispositivoView,
)

app_name = "notificaciones"

urlpatterns = [
    path("token/", RegistrarDeviceTokenView.as_view(), name="registrar-token"),
    path("demo/", EnviarNotificacionDemoView.as_view(), name="demo"),
    path("dispositivos/registrar/", RegistrarDispositivoView.as_view(), name="registrar-dispositivo"),
]
