from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient

from condominio.models import Propiedad
from seguridad.models import Visitante, Vehiculo, Visita

class ControlAccesoVehicularTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Propiedad (para residentes)
        self.user = User.objects.create_user(username="residente", password="x")
        self.prop = Propiedad.objects.create(numero_casa="1", propietario=self.user, metros_cuadrados=100)

        # Vehículo RESIDENTE
        self.residente_car = Vehiculo.objects.create(placa="RES123", propiedad=self.prop)

        # Visitante + vehículo
        self.visitante = Visitante.objects.create(
            nombres="Ana", apellidos="Ríos", documento="DNI-888", telefono="999", email="ana@test.com"
        )
        self.visitante_car = Vehiculo.objects.create(placa="VIS111", visitante=self.visitante)

        # Visita vigente hoy
        now = timezone.now()
        self.visita = Visita.objects.create(
            visitante=self.visitante,
            propiedad=self.prop,
            fecha_ingreso_programado=now - timezone.timedelta(hours=1),
            fecha_salida_programada=now + timezone.timedelta(hours=2),
        )

    def test_residente_permitido(self):
        r = self.client.post("/api/seguridad/control-acceso-vehicular/", {"placa": "RES123"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data.get("tipo"), "Residente")

    def test_visitante_permitido_y_marca_ingreso(self):
        r = self.client.post("/api/seguridad/control-acceso-vehicular/", {"placa": "VIS111"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data.get("tipo"), "Visitante")

        # Verifica que la visita marcó ingreso_real
        self.visita.refresh_from_db()
        self.assertIsNotNone(self.visita.ingreso_real)

    def test_placa_desconocida_denegado(self):
        r = self.client.post("/api/seguridad/control-acceso-vehicular/", {"placa": "NOPE999"}, format="json")
        self.assertEqual(r.status_code, 403)
