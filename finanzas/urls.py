from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IniciarPagoView, WebhookConfirmacionPagoView
from .views import (
    GastoViewSet,
    PagoViewSet,
    MultaViewSet,
    PagoMultaViewSet,
    ReservaViewSet,
    ReciboPagoPDFView,
    ReciboPagoMultaPDFView,
    ReporteMorosidadView,
    ReporteResumenView,
)

router = DefaultRouter()
router.register(r"gastos", GastoViewSet, basename="gasto")
router.register(r"pagos", PagoViewSet, basename="pago")
router.register(r"multas", MultaViewSet, basename="multa")
router.register(r"pagos_multas", PagoMultaViewSet, basename="pago-multa")
router.register(r"reservas", ReservaViewSet, basename="reserva")

urlpatterns = [
    # CRUD de DRF
    path("", include(router.urls)),

    # Comprobantes
    path("pagos/<int:pago_id>/comprobante/", ReciboPagoPDFView.as_view(), name="finanzas-pago-comprobante"),
    path("pagos-multas/<int:pago_multa_id>/comprobante/", ReciboPagoMultaPDFView.as_view(), name="finanzas-pago-multa-comprobante"),

    # Reportes
    path("reportes/estado-morosidad/", ReporteMorosidadView.as_view(), name="finanzas-reporte-morosidad"),
    path("reportes/resumen/", ReporteResumenView.as_view(), name="finanzas-reporte-resumen"),
 path('pagos/<int:pago_id>/iniciar-qr/', IniciarPagoView.as_view(), name='iniciar-pago-qr'),
    path('pagos/webhook-confirmacion/', WebhookConfirmacionPagoView.as_view(), name='webhook-pago'),
]