# seguridad/tests_permisos.py
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from django.utils import timezone
from datetime import timedelta

from condominio.models import Propiedad
from seguridad.models import Visitante, Vehiculo, Visita


class BaseAuthSetup(TestCase):
    @classmethod
    def setUpTestData(cls):
        # users
        cls.admin = User.objects.create_user(username="admin", password="x", is_staff=True, is_superuser=True)
        cls.guard = User.objects.create_user(username="guard", password="x", is_staff=False)

        cls.t_admin = Token.objects.create(user=cls.admin)
        cls.t_guard = Token.objects.create(user=cls.guard)

        # datos mínimos
        cls.p = Propiedad.objects.create(numero_casa="TEST-1", propietario=None, metros_cuadrados=80)
        cls.visit = Visitante.objects.create(nombre_completo="Ana Ríos", documento="DNI-123", telefono="9", email="a@test.com")
        cls.v_res = Vehiculo.objects.create(placa="RES111", propiedad=cls.p)
        cls.v_vis = Vehiculo.objects.create(placa="VIS222", visitante=cls.visit)

        now = timezone.now()
        Visita.objects.create(
            visitante=cls.visit,
            propiedad=cls.p,
            fecha_ingreso_programado=now - timedelta(hours=1),
            fecha_salida_programada=now + timedelta(hours=2),
            ingreso_real=now - timedelta(minutes=55),
        )

    def client_as(self, token):
        c = APIClient()
        c.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        return c


class PermissionsTests(BaseAuthSetup):
    def test_control_acceso_requires_auth(self):
        c = APIClient()  # sin auth
        r = c.post("/api/seguridad/control-acceso-vehicular/", {"placa": "RES111"}, format="json")
        self.assertEqual(r.status_code, 401)

        c2 = self.client_as(self.t_guard)
        r2 = c2.post("/api/seguridad/control-acceso-vehicular/", {"placa": "RES111"}, format="json")
        self.assertEqual(r2.status_code, 200)

    def test_export_requires_admin(self):
        # guard => 403
        c = self.client_as(self.t_guard)
        r = c.get("/api/seguridad/export/visitas.csv")
        self.assertEqual(r.status_code, 403)

        # admin => 200
        c2 = self.client_as(self.t_admin)
        r2 = c2.get("/api/seguridad/export/visitas.csv")
        self.assertEqual(r2.status_code, 200)
        self.assertIn("text/csv", r2["Content-Type"])

    def test_cerrar_visitas_vencidas_requires_admin(self):
        # guard => 403
        c = self.client_as(self.t_guard)
        r = c.post("/api/seguridad/cerrar-visitas-vencidas/", {}, format="json")
        self.assertEqual(r.status_code, 403)

        # admin => 200
        c2 = self.client_as(self.t_admin)
        r2 = c2.post("/api/seguridad/cerrar-visitas-vencidas/", {}, format="json")
        self.assertEqual(r2.status_code, 200)
        self.assertIn("cerradas", r2.data)
