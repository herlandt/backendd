from django.urls import path
from .views import RegistrarDeviceTokenView, EnviarNotificacionDemoView

app_name = "notificaciones"

urlpatterns = [
    path("registrar-token/", RegistrarDeviceTokenView.as_view(), name="registrar-token"),
    path("enviar-demo/", EnviarNotificacionDemoView.as_view(), name="enviar-demo"),
]
