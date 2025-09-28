# seguridad/management/commands/run_detector.py
from django.core.management.base import BaseCommand
from seguridad.models import Camera
from seguridad.services.detector import run_detector

class Command(BaseCommand):
    help = "Corre el detector sobre una cámara activa."

    def add_arguments(self, parser):
        parser.add_argument("--camera", required=True, help="Nombre de la cámara (p.ej. cam1)")
        parser.add_argument("--fps", type=float, default=1.0)
        parser.add_argument("--min-sim", type=float, default=90.0)

    def handle(self, *args, **opts):
        cam = Camera.objects.get(name=opts["camera"])
        self.stdout.write(self.style.SUCCESS(f"Iniciando detector en {cam.name}"))
        run_detector(cam, fps=opts["fps"], min_similarity=opts["min_sim"])
