# en seguridad/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VisitaViewSet, 
    VehiculoViewSet, 
    VisitanteViewSet, 
    EventoSeguridadViewSet,
    ControlAccesoVehicularView,
    ControlSalidaVehicularView,
    ExportVisitasCSVView,
    CerrarVisitasVencidasView,
    VisitasAbiertasView,
    DashboardResumenView,
    DashboardSeriesView,
    DashboardTopVisitantesView,
    IAControlVehicularView,
    VerificarRostroView,
    DeteccionListView,
)

router = DefaultRouter()
router.register(r'visitas', VisitaViewSet, basename='visitas')
router.register(r'vehiculos', VehiculoViewSet, basename='vehiculo')
router.register(r'visitantes', VisitanteViewSet, basename='visitante')
router.register(r'eventos', EventoSeguridadViewSet, basename='eventoseguridad')

urlpatterns = [
    path("control-acceso-vehicular/", ControlAccesoVehicularView.as_view(), name="control-acceso-vehicular"),
    path("control-salida-vehicular/", ControlSalidaVehicularView.as_view(), name="control-salida-vehicular"),
    path("visitas-abiertas/", VisitasAbiertasView.as_view(), name="visitas-abiertas"),
    path("export/visitas.csv", ExportVisitasCSVView.as_view(), name="export-visitas-csv"),
    path("cerrar-visitas-vencidas/", CerrarVisitasVencidasView.as_view(), name="cerrar-visitas-vencidas"),
    path("dashboard/resumen/", DashboardResumenView.as_view(), name="dashboard-resumen"),
    path("dashboard/series/", DashboardSeriesView.as_view(), name="dashboard-series"),
    path("dashboard/top-visitantes/", DashboardTopVisitantesView.as_view(), name="dashboard-top-visitantes"),
    path('ia/control-vehicular/', IAControlVehicularView.as_view(), name='ia-control-vehicular'),
    path('ia/verificar-rostro/', VerificarRostroView.as_view(), name='ia-verificar-rostro'),
    path("detecciones/", DeteccionListView.as_view(), name="detecciones"),
    path('', include(router.urls)),
]