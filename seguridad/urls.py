from django.urls import path
from .views import (
    ControlAccesoVehicularView,
    ControlSalidaVehicularView,
    ExportVisitasCSVView,
    CerrarVisitasVencidasView,
    CerrarVisitasVencidasView,   # <-- nuevo
    ExportVisitasCSVView,   
)

app_name = "seguridad"

urlpatterns = [
    # OJO: estos paths deben coincidir EXACTO con lo que usan los tests.
    path("control-acceso-vehicular/", ControlAccesoVehicularView.as_view(), name="control-acceso-vehicular"),
    path("control-salida-vehicular/", ControlSalidaVehicularView.as_view(), name="control-salida-vehicular"),

    # Endpoints con permisos de admin:
    path("exportar-visitas/", ExportVisitasCSVView.as_view(), name="exportar-visitas"),
    path("cerrar-visitas-vencidas/", CerrarVisitasVencidasView.as_view(), name="cerrar-visitas-vencidas"),
]
