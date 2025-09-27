from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone

from seguridad.models import Visita


class Command(BaseCommand):
    help = (
        "Cierra visitas vencidas: ingreso_real != NULL, salida_real == NULL, "
        "y fecha_salida_programada <= límite (por defecto ahora)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--hasta",
            type=str,
            help="Fecha/hora límite ISO (YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS). "
                 "Por defecto: ahora."
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Muestra cuántas cerraría sin guardar cambios."
        )

    def handle(self, *args, **opts):
        limite = timezone.now()
        if opts.get("hasta"):
            try:
                dt = datetime.fromisoformat(opts["hasta"])
            except ValueError:
                self.stderr.write(self.style.ERROR(
                    "Formato inválido para --hasta. Use YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS"
                ))
                return
            if timezone.is_naive(dt):
                limite = timezone.make_aware(dt, timezone.get_current_timezone())
            else:
                limite = dt.astimezone(timezone.get_current_timezone())

        qs = Visita.objects.filter(
            ingreso_real__isnull=False,
            salida_real__isnull=True,
            fecha_salida_programada__lte=limite,
        ).order_by("id")

        ids = list(qs.values_list("id", flat=True))
        if opts.get("dry_run"):
            self.stdout.write(self.style.WARNING(
                f"[dry-run] Cerraría {len(ids)} visitas: {ids}"
            ))
            return

        cerradas = qs.update(salida_real=limite)
        self.stdout.write(self.style.SUCCESS(
            f"Cerradas {cerradas} visitas: {ids}"
        ))
