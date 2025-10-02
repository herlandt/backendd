import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
import json

def test_api_con_permisos():
    print("TEST: API - Usuario Admin y Permisos")
    print("=" * 50)
    
    try:
        # Verificar usuario admin
        admin_user = User.objects.get(username='admin')
        print(f"Usuario admin encontrado: {admin_user.username}")
        print(f"Es staff: {admin_user.is_staff}")
        print(f"Es superuser: {admin_user.is_superuser}")
        
        # Crear cliente API
        client = APIClient()
        
        # Autenticar como admin
        token, created = Token.objects.get_or_create(user=admin_user)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        print(f"Token obtenido: {token.key[:10]}...")
        
        # Probar acceso al endpoint de residentes
        print("\nProbando GET en /api/usuarios/residentes/")
        response = client.get('/api/usuarios/residentes/')
        print(f"GET Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("EXITO: Acceso de lectura autorizado")
            
            # Intentar crear usuario sin propiedad via API
            print("\nIntentando POST en /api/usuarios/residentes/")
            data = {
                'username': 'test_api_final',
                'email': 'test_final@test.com',
                'password': 'testpass123',
                'rol': 'inquilino'
                # Sin propiedad_id
            }
            
            response = client.post('/api/usuarios/residentes/', data, format='json')
            print(f"POST Status Code: {response.status_code}")
            
            if hasattr(response, 'data'):
                print(f"Response Data: {response.data}")
            else:
                print(f"Response Content: {response.content.decode()}")
                
            if response.status_code == 201:
                print("EXITO: Usuario creado exitosamente via API")
                user_data = response.data
                print(f"   - ID: {user_data.get('id')}")
                print(f"   - Usuario: {user_data.get('usuario', {}).get('username')}")
                print(f"   - Propiedad: {user_data.get('propiedad')}")
                print(f"   - Rol: {user_data.get('rol')}")
                
                # Limpiar inmediatamente
                try:
                    user = User.objects.get(username='test_api_final')
                    user.delete()
                    print("Usuario de prueba eliminado")
                except User.DoesNotExist:
                    pass
                    
        else:
            print("ERROR: No se puede acceder al endpoint")
            
    except Exception as e:
        print(f"ERROR en Test: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\nPrueba de permisos completada!")

if __name__ == "__main__":
    test_api_con_permisos()