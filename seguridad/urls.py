from django.urls import path
from .views import (
    ControlAccesoVehicularView,
    ControlSalidaVehicularView,
    ExportVisitasCSVView,
    CerrarVisitasVencidasView,
    VisitasAbiertasView,
    DashboardResumenView,
    DashboardSeriesView,
    DashboardTopVisitantesView,
)

app_name = "seguridad"

urlpatterns = [
    # --- Endpoints de Control ---
    path("control-acceso-vehicular/", ControlAccesoVehicularView.as_view(), name="control-acceso-vehicular"),
    path("control-salida-vehicular/", ControlSalidaVehicularView.as_view(), name="control-salida-vehicular"),

    # --- Endpoints de Listas y Reportes (Admin) ---
    path("visitas-abiertas/", VisitasAbiertasView.as_view(), name="visitas-abiertas"),
    path("export/visitas.csv", ExportVisitasCSVView.as_view(), name="export-visitas-csv"), # Corregido para el test
    path("cerrar-visitas-vencidas/", CerrarVisitasVencidasView.as_view(), name="cerrar-visitas-vencidas"),

    # --- Endpoints de Dashboard (Admin) ---
    path("dashboard/resumen/", DashboardResumenView.as_view(), name="dashboard-resumen"),
    path("dashboard/series/", DashboardSeriesView.as_view(), name="dashboard-series"),
    path("dashboard/top-visitantes/", DashboardTopVisitantesView.as_view(), name="dashboard-top-visitantes"),
]