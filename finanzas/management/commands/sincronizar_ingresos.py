# finanzas/management/commands/sincronizar_ingresos.py

from django.core.management.base import BaseCommand
from django.db.models import Q
from finanzas.models import Pago, Ingreso

class Command(BaseCommand):
    help = 'Sincroniza los pagos completados antiguos para crear sus registros de Ingreso correspondientes.'

    def handle(self, *args, **kwargs):
        # Buscamos pagos que están completados pero NO tienen un ingreso asociado
        # El filtro `ingreso_manual__isnull=True` es clave aquí.
        pagos_sin_ingreso = Pago.objects.filter(
            Q(estado_pago='completado') | Q(estado_pago='PAGADO'), # Cubre ambos casos si los tienes
            ingreso_manual__isnull=True
        )

        if not pagos_sin_ingreso.exists():
            self.stdout.write(self.style.SUCCESS('¡Todo está al día! No hay pagos antiguos que sincronizar.'))
            return

        self.stdout.write(f'Se encontraron {pagos_sin_ingreso.count()} pagos completados sin registro de ingreso. Sincronizando...')

        contador = 0
        for pago in pagos_sin_ingreso:
            concepto = "Ingreso no especificado (sincronizado)"
            if pago.gasto:
                concepto = f"Pago de expensa: {pago.gasto.descripcion}"
            elif pago.multa:
                # Asegúrate de que tu modelo Multa tiene 'motivo' o ajusta el campo
                concepto = f"Pago de multa: {getattr(pago.multa, 'motivo', 'Concepto no disponible')}"
            elif pago.reserva:
                # Asegúrate de que tu modelo Reserva tiene 'area_comun' con 'nombre'
                concepto = f"Pago de reserva: {getattr(pago.reserva.area_comun, 'nombre', 'Área no disponible')}"

            Ingreso.objects.get_or_create(
                pago_relacionado=pago,
                defaults={
                    'fecha': pago.fecha_pago.date() if hasattr(pago.fecha_pago, 'date') else pago.fecha_pago,
                    'monto': pago.monto_pagado,
                    'concepto': concepto,
                    'descripcion': f"Ingreso sincronizado desde el pago ID {pago.id}"
                }
            )
            contador += 1
        
        self.stdout.write(self.style.SUCCESS(f'¡Sincronización completa! Se crearon {contador} nuevos registros de ingreso.'))