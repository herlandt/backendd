# en seguridad/tests.py

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Visita, Visitante
from usuarios.models import Residente
from condominio.models import Propiedad

class SeguridadAPITests(APITestCase):

    def setUp(self):
        self.residente_user = User.objects.create_user(username='residente', password='password123')
        self.guardia_user = User.objects.create_user(username='guardia', password='password123', is_staff=True)
        self.propiedad = Propiedad.objects.create(numero_casa='C-301', propietario=self.residente_user, metros_cuadrados=150)
        self.residente = Residente.objects.create(usuario=self.residente_user, propiedad=self.propiedad, rol='propietario')
        self.client = APIClient()
        self.visita_list_url = reverse('seguridad:visitas-list')

    def test_residente_crea_visita(self):
        self.client.force_authenticate(user=self.residente_user)
        visitante = Visitante.objects.create(nombre_completo='Pedro Pascal', documento='1234567 LP')
        data = {
            'visitante': visitante.id,
            'propiedad': self.propiedad.id,
            'fecha_ingreso_programado': '2025-10-05T14:00:00Z',
            'fecha_salida_programada': '2025-10-05T18:00:00Z',
        }
        response = self.client.post(self.visita_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Visita.objects.count(), 1)

    def test_guardia_actualiza_ingreso_real_de_visita(self):
        visitante = Visitante.objects.create(nombre_completo='Ana de Armas', documento='987654 SC')
        visita = Visita.objects.create(
            visitante=visitante,
            propiedad=self.propiedad,
            fecha_ingreso_programado=timezone.now(),
            fecha_salida_programada=timezone.now() + timezone.timedelta(hours=4)
        )
        self.client.force_authenticate(user=self.guardia_user)
        detail_url = reverse('seguridad:visitas-detail', kwargs={'pk': visita.pk})
        data = {'ingreso_real': timezone.now()}
        response = self.client.patch(detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        visita.refresh_from_db()
        self.assertIsNotNone(visita.ingreso_real)