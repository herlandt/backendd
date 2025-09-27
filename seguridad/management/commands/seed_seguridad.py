# seguridad/management/commands/seed_seguridad.py
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from condominio.models import Propiedad
from seguridad.models import Visitante, Vehiculo, Visita


class Command(BaseCommand):
    help = "Carga datos de ejemplo para seguridad (residente, visitante y una visita vigente)."

    def handle(self, *args, **options):
        now = timezone.now()

        # Propiedad
        p, _ = Propiedad.objects.get_or_create(
            numero_casa="A-101",
            defaults={"propietario": None, "metros_cuadrados": 120},
        )

        # Visitante
        visit, _ = Visitante.objects.get_or_create(
            documento="DNI-888",
            defaults={"nombre_completo": "Ana Ríos", "telefono": "999", "email": "ana@test.com"},
        )

        # Vehículo residente
        v_res, _ = Vehiculo.objects.get_or_create(placa="ABC123", defaults={"propiedad": p})
        if v_res.visitante_id is not None or v_res.propiedad_id != p.id:
            v_res.visitante = None
            v_res.propiedad = p
            v_res.save(update_fields=["visitante", "propiedad"])

        # Vehículo visitante
        v_vis, _ = Vehiculo.objects.get_or_create(placa="XYZ789", defaults={"visitante": visit})
        if v_vis.propiedad_id is not None or v_vis.visitante_id != visit.id:
            v_vis.propiedad = None
            v_vis.visitante = visit
            v_vis.save(update_fields=["visitante", "propiedad"])

        # Visita vigente (cubre "ahora")
        inicio = now - timedelta(hours=1)
        fin = now + timedelta(hours=2)
        visita = (
            Visita.objects
            .filter(visitante=visit, propiedad=p, fecha_salida_programada__gte=now)
            .order_by("-fecha_ingreso_programado")
            .first()
        )
        if visita is None:
            visita = Visita.objects.create(
                visitante=visit,
                propiedad=p,
                fecha_ingreso_programado=inicio,
                fecha_salida_programada=fin,
            )
        else:
            to_update = []
            if visita.fecha_ingreso_programado > inicio:
                visita.fecha_ingreso_programado = inicio
                to_update.append("fecha_ingreso_programado")
            if visita.fecha_salida_programada < fin:
                visita.fecha_salida_programada = fin
                to_update.append("fecha_salida_programada")
            if to_update:
                visita.save(update_fields=to_update)

        self.stdout.write(
            self.style.SUCCESS(
                f"OK: propiedad={p.id}, vehiculo_residente={v_res.id}, "
                f"visitante={visit.id}, vehiculo_visitante={v_vis.id}, visita={visita.id}"
            )
        )
    