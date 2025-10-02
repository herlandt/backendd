import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from condominio.models import Propiedad
from usuarios.models import Residente

class TestUsuarioSinPropiedad(APITestCase):
    def setUp(self):
        # Crear admin
        self.admin_user = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='adminpass123'
        )
        
        # Autenticar cliente
        self.client.force_authenticate(user=self.admin_user)
        
    def test_crear_residente_sin_propiedad(self):
        """Test: Crear residente sin propiedad usando API"""
        print("TEST: Crear residente sin propiedad via API")
        
        data = {
            "username": "sin_propiedad",
            "email": "sinprop@example.com", 
            "password": "strongpassword123",
            "rol": "inquilino"
            # NO incluir propiedad_id
        }
        
        response = self.client.post('/api/usuarios/residentes/', data, format='json')
        
        print(f"Status: {response.status_code}")
        
        if response.status_code != 201:
            print(f"Error: {response.data}")
        
        # Verificar respuesta exitosa
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que el usuario se creó
        self.assertTrue(User.objects.filter(username='sin_propiedad').exists())
        
        # Verificar que el residente se creó sin propiedad
        residente = Residente.objects.get(usuario__username='sin_propiedad')
        self.assertIsNone(residente.propiedad)
        self.assertEqual(residente.rol, 'inquilino')
        
        print("✅ Test exitoso: Usuario creado sin propiedad")

if __name__ == "__main__":
    # Ejecutar test individual
    test = TestUsuarioSinPropiedad()
    test.setUp()
    test.test_crear_residente_sin_propiedad()