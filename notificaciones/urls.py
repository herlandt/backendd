from django.urls import path
from .views import RegistrarDeviceTokenView, EnviarNotificacionDemoView,RegistrarDispositivoView

app_name = "notificaciones"

urlpatterns = [
    path("registrar-token/", RegistrarDeviceTokenView.as_view(), name="registrar-token"),
    path("enviar-demo/", EnviarNotificacionDemoView.as_view(), name="enviar-demo"),
  path('registrar-dispositivo/', RegistrarDispositivoView.as_view(), name='registrar-dispositivo'),
]