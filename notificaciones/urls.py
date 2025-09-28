from django.urls import path
from .views import RegistrarDeviceTokenView, EnviarNotificacionDemoView, RegistrarDispositivoView

urlpatterns = [
    path("token/", RegistrarDeviceTokenView.as_view(), name="registrar-device-token"),
    path("demo/",  EnviarNotificacionDemoView.as_view(), name="enviar-notificacion-demo"),
    path("registrar-dispositivo/", RegistrarDispositivoView.as_view(), name="registrar-dispositivo"),
]
