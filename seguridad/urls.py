from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    VisitanteViewSet, VehiculoViewSet, VisitaViewSet,
    ControlAccesoVehicular, ControlSalidaVehicular,
    VisitasAbiertasView, CerrarVisitasVencidas, ExportVisitasCSV,
    DashboardResumenView, DashboardSeriesView, DashboardTopVisitantes,  # 👈 usa las nuevas
)

router = DefaultRouter()
router.register(r"visitantes", VisitanteViewSet, basename="visitante")
router.register(r"vehiculos",  VehiculoViewSet,  basename="vehiculo")
router.register(r"visitas",    VisitaViewSet,    basename="visita")

urlpatterns = [
    path("", include(router.urls)),
    path("control-acceso-vehicular/", ControlAccesoVehicular.as_view(), name="control-acceso-vehicular"),
    path("control-salida-vehicular/",  ControlSalidaVehicular.as_view(),  name="control-salida-vehicular"),
    path("visitas-abiertas/",          VisitasAbiertasView.as_view(),     name="visitas-abiertas"),
    path("cerrar-visitas-vencidas/",   CerrarVisitasVencidas.as_view(),   name="cerrar-visitas-vencidas"),

    # Export
    path("export/visitas.csv",         ExportVisitasCSV.as_view(),        name="export-visitas-csv"),

    # Dashboard (👈 aquí el cambio)
    path("dashboard/resumen/",         DashboardResumenView.as_view(),    name="dashboard-resumen"),
    path("dashboard/series/",          DashboardSeriesView.as_view(),     name="dashboard-series"),
    path("dashboard/top-visitantes/",  DashboardTopVisitantes.as_view(),  name="dashboard-top-visitantes"),
     path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
]
