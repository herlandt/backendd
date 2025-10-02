import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import UserProfile, Residente
from usuarios.serializers import ResidenteWriteSerializer

def test_usuario_sin_propiedad():
    print("TEST: Creacion de Usuario sin Propiedad")
    print("=" * 50)
    
    # Test 1: Crear usuario sin propiedad usando serializer
    try:
        print("\nTest 1: Creacion con serializer...")
        
        data = {
            'username': 'test_sin_prop',
            'email': 'test@test.com',
            'password': 'testpass123',
            'rol': 'inquilino'
            # Sin propiedad_id
        }
        
        serializer = ResidenteWriteSerializer(data=data)
        
        if serializer.is_valid():
            residente = serializer.save()
            print(f"EXITO: Usuario creado con serializer:")
            print(f"   - ID: {residente.id}")
            print(f"   - Usuario: {residente.usuario.username}")
            print(f"   - Propiedad: {residente.propiedad}")
            print(f"   - Rol: {residente.rol}")
        else:
            print(f"ERROR: Errores de validacion: {serializer.errors}")
            
    except Exception as e:
        print(f"ERROR en Test 1: {str(e)}")
    
    # Limpiar
    try:
        user = User.objects.get(username='test_sin_prop')
        user.delete()
        print("Usuario de prueba eliminado")
    except User.DoesNotExist:
        pass
    
    print("\nPruebas completadas!")

if __name__ == "__main__":
    test_usuario_sin_propiedad()