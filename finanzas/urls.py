from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    # viewsets
    GastoViewSet, PagoViewSet, MultaViewSet, PagoMultaViewSet, ReservaViewSet,
    # comprobantes
    ReciboPagoPDFView, ReciboPagoMultaPDFView,
    # reportes
    ReporteMorosidadView, ReporteResumenView,
    # pagos / reservas
    IniciarPagoView, SimularPagoView, WebhookConfirmacionPagoView, PagarReservaView,
    # utilidades finanzas
    GenerarExpensasView, EstadoDeCuentaView,
    EgresoViewSet, IngresoViewSet, ReporteFinancieroView,ReporteUsoAreasComunesView 
)

router = DefaultRouter()
router.register(r"gastos", GastoViewSet, basename="gasto")
router.register(r"pagos", PagoViewSet, basename="pago")  # Restaurado
router.register(r"multas", MultaViewSet, basename="multa")
router.register(r"pagos-multas", PagoMultaViewSet, basename="pago-multa")
router.register(r"reservas", ReservaViewSet, basename="reserva")
router.register(r'egresos', EgresoViewSet, basename='egresos')
router.register(r'ingresos', IngresoViewSet, basename='ingresos')


urlpatterns = [
    # CRUDs
    path("", include(router.urls)),

    # Comprobantes
    path("pagos/<int:pago_id>/comprobante/", ReciboPagoPDFView.as_view(), name="finanzas-pago-comprobante"),
    path("pagos-multas/<int:pago_multa_id>/comprobante/", ReciboPagoMultaPDFView.as_view(), name="finanzas-pago-multa-comprobante"),

    # Reportes
    path("reportes/estado-morosidad/", ReporteMorosidadView.as_view(), name="finanzas-reporte-morosidad"),
    path("reportes/resumen/", ReporteResumenView.as_view(), name="finanzas-reporte-resumen"),

    # Pasarela (demo)
   # path("pagos/<int:pago_id>/iniciar/", IniciarPagoView.as_view(), name="iniciar-pago"),
    path("pagos/<int:pago_id>/simular/", SimularPagoView.as_view(), name="simular-pago"),
    path("webhook/pagosnet/", WebhookConfirmacionPagoView.as_view(), name="webhook-pagosnet"),

    # Pagar reserva vía pasarela (demo)
    path("reservas/<int:reserva_id>/pagar/", PagarReservaView.as_view(), name="pagar-reserva"),

    # Utilidades admin/usuario
    path("expensas/generar/", GenerarExpensasView.as_view(), name="generar-expensas"),
    path("estado-de-cuenta/", EstadoDeCuentaView.as_view(), name="estado-de-cuenta"),
 path('reportes/financiero/', ReporteFinancieroView.as_view(), name='reporte-financiero'),
path('reportes/uso-areas-comunes/', ReporteUsoAreasComunesView.as_view(), name='reporte-uso-areas-comunes'),
]