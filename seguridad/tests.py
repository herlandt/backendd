from datetime import timedelta

from django.test import TestCase
from django.urls import reverse, NoReverseMatch
from django.utils import timezone

from condominio.models import Propiedad
from .models import Visitante, Vehiculo, Visita


class ControlAccesoVehicularTests(TestCase):
    def setUp(self):
        # Datos base
        self.prop = Propiedad.objects.create(
            numero_casa="1",
            metros_cuadrados=100,
        )

        self.visitante = Visitante.objects.create(
            nombre_completo="Ana Ríos",
            documento="DNI-888",
            telefono="999",
            email="ana@test.com",
        )

        # Vehículo residente (sin visitante, con propiedad)
        self.veh_res = Vehiculo.objects.create(
            placa="ABC123", propiedad=self.prop
        )

        # Vehículo visitante (con visitante, sin propiedad)
        self.veh_vis = Vehiculo.objects.create(
            placa="XYZ789", visitante=self.visitante
        )

        # Visita vigente hoy
        ahora = timezone.now()
        self.visita = Visita.objects.create(
            visitante=self.visitante,
            propiedad=self.prop,
            fecha_ingreso_programado=ahora - timedelta(hours=1),
            fecha_salida_programada=ahora + timedelta(hours=2),
        )

        # URL del endpoint (con o sin namespace)
        try:
            self.url = reverse("seguridad:control-acceso-vehicular")
        except NoReverseMatch:
            self.url = reverse("control-acceso-vehicular")

    def test_residente_permitido(self):
        resp = self.client.post(self.url, {"placa": "ABC123"}, content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get("tipo"), "Residente")

    def test_visitante_permitido_y_marca_ingreso(self):
        resp = self.client.post(self.url, {"placa": "XYZ789"}, content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get("tipo"), "Visitante")

        self.visita.refresh_from_db()
        self.assertIsNotNone(self.visita.ingreso_real)

    def test_placa_desconocida_denegado(self):
        resp = self.client.post(self.url, {"placa": "ZZZ999"}, content_type="application/json")
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.json().get("status"), "Acceso Denegado")
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from condominio.models import Propiedad
from seguridad.models import Visitante, Vehiculo, Visita


class ControlSalidaVehicularTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url_acceso = reverse("seguridad:control-acceso-vehicular")
        self.url_salida = reverse("seguridad:control-salida-vehicular")

        # Datos base
        self.p = Propiedad.objects.create(numero_casa="A-101", propietario=None, metros_cuadrados=120)
        self.visit = Visitante.objects.create(
            nombre_completo="Ana Ríos", documento="DNI-888", telefono="999", email="ana@test.com"
        )
        # Vehículos
        self.v_res = Vehiculo.objects.create(placa="ABC123", propiedad=self.p)
        self.v_vis = Vehiculo.objects.create(placa="XYZ789", visitante=self.visit)

        # Visita vigente (para el visitante)
        now = timezone.now()
        self.visita = Visita.objects.create(
            visitante=self.visit,
            propiedad=self.p,
            fecha_ingreso_programado=now - timedelta(hours=1),
            fecha_salida_programada=now + timedelta(hours=2),
        )

    def test_salida_visitante_sin_ingreso_denegada(self):
        # Intentar salir sin haber registrado ingreso
        r = self.client.post(self.url_salida, {"placa": "XYZ789"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.data["permitido"])
        self.assertIn("No hay registro de ingreso", r.data["motivo"])

    def test_salida_visitante_cierra_visita(self):
        # Primero registrar ingreso
        r1 = self.client.post(self.url_acceso, {"placa": "XYZ789"}, format="json")
        self.assertEqual(r1.status_code, 200)
        self.assertTrue(r1.data["permitido"])

        # Luego salida
        r2 = self.client.post(self.url_salida, {"placa": "XYZ789"}, format="json")
        self.assertEqual(r2.status_code, 200)
        self.assertTrue(r2.data["permitido"])
        self.visita.refresh_from_db()
        self.assertIsNotNone(self.visita.salida_real)

    def test_salida_residente_ok(self):
        r = self.client.post(self.url_salida, {"placa": "ABC123"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.data["permitido"])
        self.assertEqual(r.data["tipo"], "residente")
