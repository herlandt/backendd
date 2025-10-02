import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
import json

def test_api_usuario_sin_propiedad():
    print("TEST: API - Creacion de Usuario sin Propiedad")
    print("=" * 50)
    
    try:
        # Crear cliente API
        client = APIClient()
        
        # Autenticar como admin
        admin_user = User.objects.get(username='admin')
        token, created = Token.objects.get_or_create(user=admin_user)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        # Intentar crear usuario sin propiedad via API
        data = {
            'username': 'test_api_sin_prop',
            'email': 'test_api@test.com',
            'password': 'testpass123',
            'rol': 'inquilino'
            # Sin propiedad_id
        }
        
        response = client.post('/api/usuarios/residentes/', data, format='json')
        
        print(f"Status Code: {response.status_code}")
        
        if hasattr(response, 'data'):
            print(f"Response Data: {response.data}")
        else:
            print(f"Response Content: {response.content.decode()}")
        
        if response.status_code == 201:
            print("EXITO: Usuario creado exitosamente via API")
        elif response.status_code == 400:
            print("ERROR 400: Datos invalidos - veamos que campos faltan")
        else:
            print(f"ERROR {response.status_code}: Error inesperado")
            
    except Exception as e:
        print(f"ERROR en Test API: {str(e)}")
    
    print("\nPrueba API completada!")

if __name__ == "__main__":
    test_api_usuario_sin_propiedad()