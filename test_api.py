import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

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
        
        response = client.post('/api/usuarios/residentes/', data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.data}")
        
        if response.status_code == 201:
            print("EXITO: Usuario creado exitosamente via API")
            
            # Verificar datos
            user_data = response.data
            print(f"   - ID: {user_data.get('id')}")
            print(f"   - Usuario: {user_data.get('usuario', {}).get('username')}")
            print(f"   - Propiedad: {user_data.get('propiedad')}")
            print(f"   - Rol: {user_data.get('rol')}")
        else:
            print("ERROR: No se pudo crear usuario via API")
            
    except Exception as e:
        print(f"ERROR en Test API: {str(e)}")
    
    # Limpiar
    try:
        user = User.objects.get(username='test_api_sin_prop')
        user.delete()
        print("Usuario de prueba API eliminado")
    except User.DoesNotExist:
        pass
    
    print("\nPrueba API completada!")

if __name__ == "__main__":
    test_api_usuario_sin_propiedad()