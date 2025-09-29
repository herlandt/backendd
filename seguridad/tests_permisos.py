# en seguridad/tests_permisos.py

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from condominio.models import Propiedad

class PermissionsTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'password123')
        cls.staff_user = User.objects.create_user('staff', 'staff@example.com', 'password123', is_staff=True)
        cls.normal_user = User.objects.create_user('user', 'user@example.com', 'password123')
        cls.p = Propiedad.objects.create(numero_casa="TEST-1", propietario=cls.normal_user, metros_cuadrados=80)
        cls.url_control_acceso = reverse('seguridad:control-acceso-vehicular')


    def test_staff_can_access_endpoint(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(self.url_control_acceso, {"placa": "NOEXISTE"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_normal_user_cannot_access_endpoint(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post(self.url_control_acceso, {"placa": "NOEXISTE"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)