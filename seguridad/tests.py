from datetime import timedelta
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token  # <-- CORRECCIÓN AQUÍ
from condominio.models import Propiedad
from .models import Visitante, Vehiculo, Visita

# --- BASE CLASS CON AUTENTICACIÓN ---
class BaseSeguridadTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_user("admin", "admin@test.com", "pass", is_staff=True, is_superuser=True)
        cls.guard_user = User.objects.create_user("guardia", "guardia@test.com", "pass")
        cls.admin_token = Token.objects.create(user=cls.admin_user)
        cls.guard_token = Token.objects.create(user=cls.guard_user)

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.guard_token.key}')

# --- TESTS ---

class ControlAccesoVehicularTests(BaseSeguridadTestCase):
    def setUp(self):
        super().setUp()
        self.prop = Propiedad.objects.create(numero_casa="1", metros_cuadrados=100)
        self.visitante = Visitante.objects.create(nombre_completo="Ana Ríos", documento="DNI-888")
        self.veh_res = Vehiculo.objects.create(placa="ABC123", propiedad=self.prop)
        self.veh_vis = Vehiculo.objects.create(placa="XYZ789", visitante=self.visitante)
        ahora = timezone.now()
        self.visita = Visita.objects.create(
            visitante=self.visitante, propiedad=self.prop,
            fecha_ingreso_programado=ahora - timedelta(hours=1),
            fecha_salida_programada=ahora + timedelta(hours=1),
        )
        self.url = reverse("seguridad:control-acceso-vehicular")

    def test_residente_permitido(self):
        resp = self.client.post(self.url, {"placa": "ABC123"})
        self.assertEqual(resp.status_code, 200)

    def test_visitante_permitido_y_marca_ingreso(self):
        resp = self.client.post(self.url, {"placa": "XYZ789"})
        self.assertEqual(resp.status_code, 200)
        self.visita.refresh_from_db()
        self.assertIsNotNone(self.visita.ingreso_real)

    def test_placa_desconocida_denegado(self):
        resp = self.client.post(self.url, {"placa": "NOEXISTE"})
        self.assertEqual(resp.status_code, 403)

class ControlSalidaVehicularTests(BaseSeguridadTestCase):
    def setUp(self):
        super().setUp()
        self.prop = Propiedad.objects.create(numero_casa="2", metros_cuadrados=100)
        self.visitante = Visitante.objects.create(nombre_completo="Beto Soliz", documento="DNI-999")
        self.veh_res = Vehiculo.objects.create(placa="RES456", propiedad=self.prop)
        self.veh_vis = Vehiculo.objects.create(placa="VIS654", visitante=self.visitante)
        self.visita_activa = Visita.objects.create(
            visitante=self.visitante, propiedad=self.prop,
            fecha_ingreso_programado=timezone.now() - timedelta(hours=2),
            fecha_salida_programada=timezone.now() + timedelta(hours=2),
            ingreso_real=timezone.now() - timedelta(hours=1)
        )
        self.url = reverse("seguridad:control-salida-vehicular")

    def test_salida_visitante_cierra_visita(self):
        r1 = self.client.post(self.url, {"placa": "VIS654"})
        self.assertEqual(r1.status_code, 200)
        self.visita_activa.refresh_from_db()
        self.assertIsNotNone(self.visita_activa.salida_real)

    def test_salida_residente_ok(self):
        r = self.client.post(self.url, {"placa": "RES456"})
        self.assertEqual(r.status_code, 200)

    def test_salida_visitante_sin_ingreso_denegada(self):
        visitante_nuevo = Visitante.objects.create(nombre_completo="Daniel Solis", documento="DNI-222")
        vehiculo_nuevo = Vehiculo.objects.create(placa="OTRAPLACA", visitante=visitante_nuevo)
        Visita.objects.create(
            visitante=visitante_nuevo, propiedad=self.prop,
            fecha_ingreso_programado=timezone.now(),
            fecha_salida_programada=timezone.now() + timedelta(hours=2)
        )
        r = self.client.post(self.url, {"placa": "OTRAPLACA"})
        self.assertEqual(r.status_code, 404)


class VisitasAbiertasViewTests(BaseSeguridadTestCase):
    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        self.url = reverse("seguridad:visitas-abiertas")
        self.prop = Propiedad.objects.create(numero_casa="3", metros_cuadrados=100)
        self.visitante = Visitante.objects.create(nombre_completo="Ceci Tapia", documento="DNI-111")
        Visita.objects.create(
            visitante=self.visitante, propiedad=self.prop,
            fecha_ingreso_programado=timezone.now(), fecha_salida_programada=timezone.now(),
            ingreso_real=timezone.now()
        )
        Visita.objects.create(
            visitante=self.visitante, propiedad=self.prop,
            fecha_ingreso_programado=timezone.now(), fecha_salida_programada=timezone.now(),
            ingreso_real=timezone.now(), salida_real=timezone.now()
        )

    def test_lista_solo_abiertas(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 1)


class PermissionsTests(BaseSeguridadTestCase):
    def test_cerrar_visitas_vencidas_requires_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.guard_token.key}")
        r1 = self.client.post(reverse("seguridad:cerrar-visitas-vencidas"))
        self.assertEqual(r1.status_code, 403)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        r2 = self.client.post(reverse("seguridad:cerrar-visitas-vencidas"))
        self.assertEqual(r2.status_code, 200)
        self.assertIn("Comando para cerrar visitas vencidas ejecutado", r2.data["detail"])