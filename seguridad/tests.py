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


# seguridad/tests.py
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from condominio.models import Propiedad
from seguridad.models import Visitante, Visita

class DashboardEndpointsTests(APITestCase):
    def setUp(self):
        self.prop = Propiedad.objects.create(numero_casa="T-1", propietario=None, metros_cuadrados=80)
        self.visit = Visitante.objects.create(nombre_completo="Test V", documento="TEST-1")
        now = timezone.now()

        # programada hoy, con ingreso y salida hoy
        Visita.objects.create(
            visitante=self.visit,
            propiedad=self.prop,
            fecha_ingreso_programado=now - timedelta(hours=1),
            fecha_salida_programada=now + timedelta(hours=1),
            ingreso_real=now - timedelta(minutes=30),
            salida_real=now - timedelta(minutes=5),
        )
        # abierta y vencida
        Visita.objects.create(
            visitante=self.visit,
            propiedad=self.prop,
            fecha_ingreso_programado=now - timedelta(days=1, hours=2),
            fecha_salida_programada=now - timedelta(hours=1),
            ingreso_real=now - timedelta(days=1),
            salida_real=None,
        )

    def test_dashboard_resumen(self):
        r = self.client.get("/api/seguridad/dashboard/resumen/")
        self.assertEqual(r.status_code, 200)
        for key in ["programadas", "ingresos", "salidas", "abiertas", "vencidas_abiertas", "visitantes_unicos", "fecha"]:
            self.assertIn(key, r.data)

    def test_dashboard_series(self):
        today = timezone.localdate()
        r = self.client.get(f"/api/seguridad/dashboard/series/?from={today}&to={today}")
        self.assertEqual(r.status_code, 200)
        self.assertIn("items", r.data)
        self.assertTrue(len(r.data["items"]) >= 1)
        day = r.data["items"][0]
        for key in ["date", "programadas", "ingresos", "salidas"]:
            self.assertIn(key, day)
# ======== TESTS ADICIONALES ========

from django.urls import reverse
from django.utils import timezone
from datetime import timedelta


class VisitasAbiertasViewTests(TestCase):
    def setUp(self):
        self.url = reverse("seguridad:visitas-abiertas")
        self.prop = Propiedad.objects.create(numero_casa="A-9", metros_cuadrados=90)
        self.vis = Visitante.objects.create(nombre_completo="Open V", documento="DOC-OPEN")
        now = timezone.now()

        # 1 abierta (ingreso_real != None, salida_real == None)
        self.v_abierta = Visita.objects.create(
            visitante=self.vis,
            propiedad=self.prop,
            fecha_ingreso_programado=now - timedelta(hours=2),
            fecha_salida_programada=now + timedelta(hours=2),
            ingreso_real=now - timedelta(hours=1),
            salida_real=None,
        )
        # 1 cerrada
        Visita.objects.create(
            visitante=self.vis,
            propiedad=self.prop,
            fecha_ingreso_programado=now - timedelta(days=1, hours=2),
            fecha_salida_programada=now - timedelta(days=1, hours=1),
            ingreso_real=now - timedelta(days=1, hours=2),
            salida_real=now - timedelta(days=1, hours=1),
        )
        # 1 sin ingreso aún
        Visita.objects.create(
            visitante=self.vis,
            propiedad=self.prop,
            fecha_ingreso_programado=now + timedelta(hours=1),
            fecha_salida_programada=now + timedelta(hours=3),
            ingreso_real=None,
            salida_real=None,
        )

    def test_lista_solo_abiertas(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)

        data = r.json()  # lista de visitas abiertas
        self.assertEqual(len(data), 1)
        item = data[0]
        # claves esperadas en la respuesta
        for key in ["id", "visitante", "documento", "propiedad", "ingreso_real", "salida_programada"]:
            self.assertIn(key, item)
        self.assertEqual(item["id"], self.v_abierta.id)


class CerrarVisitasVencidasTests(TestCase):
    def setUp(self):
        self.url = reverse("seguridad:cerrar-visitas-vencidas")
        self.prop = Propiedad.objects.create(numero_casa="B-1", metros_cuadrados=100)
        self.vis = Visitante.objects.create(nombre_completo="Vencida", documento="DOC-VENC")
        now = timezone.now()

        # Expirada (debe cerrarse): salida_programada < now
        self.v_expirada = Visita.objects.create(
            visitante=self.vis,
            propiedad=self.prop,
            fecha_ingreso_programado=now - timedelta(hours=4),
            fecha_salida_programada=now - timedelta(hours=2),
            ingreso_real=now - timedelta(hours=3),
            salida_real=None,
        )
        # Abierta pero no vencida (no debe cerrarse)
        self.v_abierta = Visita.objects.create(
            visitante=self.vis,
            propiedad=self.prop,
            fecha_ingreso_programado=now - timedelta(hours=1),
            fecha_salida_programada=now + timedelta(hours=2),
            ingreso_real=now - timedelta(minutes=30),
            salida_real=None,
        )

    def test_cierra_solo_las_vencidas(self):
        r = self.client.post(self.url, {})
        self.assertEqual(r.status_code, 200)
        self.assertIn("cerradas", r.json())
        self.assertEqual(r.json()["cerradas"], 1)

        # refrescar de BD
        self.v_expirada.refresh_from_db()
        self.v_abierta.refresh_from_db()

        # La expirada debe quedar con salida_real igual a fecha_salida_programada
        self.assertIsNotNone(self.v_expirada.salida_real)
        self.assertEqual(
            self.v_expirada.salida_real.replace(microsecond=0),
            self.v_expirada.fecha_salida_programada.replace(microsecond=0),
        )
        # La no vencida debe seguir abierta
        self.assertIsNone(self.v_abierta.salida_real)


class ExportVisitasCSVTests(TestCase):
    def setUp(self):
        self.url = reverse("seguridad:export-visitas-csv")
        self.prop = Propiedad.objects.create(numero_casa="C-3", metros_cuadrados=80)
        self.vis = Visitante.objects.create(nombre_completo="CSV Tester", documento="DOC-CSV")
        now = timezone.now()

        self.v = Visita.objects.create(
            visitante=self.vis,
            propiedad=self.prop,
            fecha_ingreso_programado=now - timedelta(hours=2),
            fecha_salida_programada=now + timedelta(hours=2),
            ingreso_real=now - timedelta(hours=1),
            salida_real=None,
        )

    def test_exporta_csv_con_fila(self):
        from datetime import date
        import io, csv

        # Rango amplio que incluye la visita creada
        params = {
            "from": (timezone.localdate() - timedelta(days=1)).isoformat(),
            "to": (timezone.localdate() + timedelta(days=1)).isoformat(),
        }
        r = self.client.get(self.url, params)
        self.assertEqual(r.status_code, 200)
        self.assertIn("text/csv", r.headers.get("Content-Type", ""))

        # Parsear CSV
        content = r.content.decode("utf-8")
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        # Primera fila: encabezados
        self.assertGreaterEqual(len(rows), 2)
        header = rows[0]
        self.assertIn("id", header)
        self.assertIn("visitante_documento", header)
        # Debe incluir nuestro ID
        ids = [row[0] for row in rows[1:] if row]
        self.assertIn(str(self.v.id), ids)


class DashboardTopVisitantesTests(TestCase):
    def setUp(self):
        self.url = reverse("seguridad:dashboard-top-visitantes")
        self.prop = Propiedad.objects.create(numero_casa="D-4", metros_cuadrados=120)
        now = timezone.now()

        self.v1 = Visitante.objects.create(nombre_completo="Carlos", documento="DOC-C1")
        self.v2 = Visitante.objects.create(nombre_completo="Ana", documento="DOC-A1")

        # Carlos con 3 visitas
        for i in range(3):
            Visita.objects.create(
                visitante=self.v1,
                propiedad=self.prop,
                fecha_ingreso_programado=now - timedelta(days=i),
                fecha_salida_programada=now + timedelta(days=1),
            )

        # Ana con 1 visita
        Visita.objects.create(
            visitante=self.v2,
            propiedad=self.prop,
            fecha_ingreso_programado=now,
            fecha_salida_programada=now + timedelta(days=1),
        )

    def test_top_visitantes_basico(self):
        r = self.client.get(self.url, {"days": 30, "limit": 2})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("items", data)
        items = data["items"]
        self.assertLessEqual(len(items), 2)

        # Debe estar Carlos primero con 3
        self.assertGreaterEqual(len(items), 1)
        self.assertEqual(items[0]["nombre"], "Carlos")
        self.assertEqual(items[0]["visitas"], 3)
        # y Ana con 1
        if len(items) > 1:
            self.assertEqual(items[1]["nombre"], "Ana")
            self.assertEqual(items[1]["visitas"], 1)
