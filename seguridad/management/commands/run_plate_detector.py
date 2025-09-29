from django.core.management.base import BaseCommand
from seguridad.models import Camera
from seguridad.services.detector import run_plate_detector

class Command(BaseCommand):
    help = 'Inicia el detector de matrículas para una cámara específica'

    def add_arguments(self, parser):
        parser.add_argument('--camera', type=str, help='Nombre de la cámara a monitorear')

    def handle(self, *args, **options):
        camera_name = options.get('camera')
        if not camera_name:
            self.stdout.write(self.style.ERROR('Debe especificar el nombre de la cámara con --camera'))
            return

        try:
            camera = Camera.objects.get(name=camera_name, active=True)
        except Camera.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"No se encontró una cámara activa con el nombre '{camera_name}'"))
            return

        self.stdout.write(self.style.SUCCESS(f"Iniciando detector de matrículas para la cámara: {camera.name}"))
        run_plate_detector(camera)