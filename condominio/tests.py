# en condominio/tests.py

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Propiedad, AreaComun

class CondominioAPITests(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_user(username='admin', password='password123', is_staff=True)
        self.propietario = User.objects.create_user(username='propietario', password='password123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)
        
        self.propiedad_list_url = reverse('propiedad-list')
        self.areacomun_list_url = reverse('areacomun-list')

    def test_admin_crea_propiedad(self):
        """Prueba que un admin puede registrar una nueva propiedad."""
        data = {
            'numero_casa': 'E-501',
            'metros_cuadrados': 250.75,
            'propietario_id': self.propietario.id # Corregido: Usamos el campo write_only 'propietario_id'
        }
        response = self.client.post(self.propiedad_list_url, data, format='json')
        
        if response.status_code != status.HTTP_201_CREATED:
            print("Error creando propiedad:", response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Propiedad.objects.count(), 1)
        self.assertEqual(Propiedad.objects.get().propietario, self.propietario)

    def test_listar_areas_comunes(self):
        """Prueba que se pueden listar las áreas comunes (GET), ya que POST no está permitido."""
        AreaComun.objects.create(nombre='Salón de Eventos', capacidad=100, descripcion="Salón principal")
        
        response = self.client.get(self.areacomun_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre'], 'Salón de Eventos')