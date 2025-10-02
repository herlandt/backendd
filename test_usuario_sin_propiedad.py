#!/usr/bin/env python
"""
🧪 TEST: Creación de Usuario sin Propiedad
==========================================

Verifica que se pueda crear un usuario sin asignar una propiedad,
después de los cambios realizados en el modelo y serializer.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import UserProfile, Residente
from usuarios.serializers import ResidenteWriteSerializer

def test_usuario_sin_propiedad():
    """Prueba crear un usuario residente sin propiedad asignada"""
    
    print("🧪 PRUEBA: Creación de Usuario sin Propiedad")
    print("=" * 50)
    
    # Test 1: Crear usuario sin propiedad usando el modelo directamente
    try:
        print("\n📝 Test 1: Creación directa con modelo...")
        
        # Crear usuario base
        user = User.objects.create_user(
            username='test_sin_propiedad',
            email='test@test.com',
            password='testpass123'
        )
        
        # Crear residente sin propiedad
        residente = Residente.objects.create(
            usuario=user,
            propiedad=None,  # ✅ Explícitamente sin propiedad
            rol='inquilino'
        )
        
        print(f"✅ Usuario creado exitosamente:")
        print(f"   - ID: {residente.id}")
        print(f"   - Usuario: {residente.usuario.username}")
        print(f"   - Propiedad: {residente.propiedad}")
        print(f"   - Rol: {residente.rol}")
        
    except Exception as e:
        print(f"❌ Error en Test 1: {str(e)}")
    
    # Test 2: Crear usuario sin propiedad usando serializer
    try:
        print("\n📝 Test 2: Creación con serializer...")
        
        data = {
            'username': 'test_serializer_sin_prop',
            'email': 'test_serializer@test.com',
            'password': 'testpass123',
            'rol': 'inquilino'
            # ✅ Nota: NO incluimos propiedad_id
        }
        
        serializer = ResidenteWriteSerializer(data=data)
        
        if serializer.is_valid():
            residente = serializer.save()
            print(f"✅ Usuario creado con serializer:")
            print(f"   - ID: {residente.id}")
            print(f"   - Usuario: {residente.usuario.username}")
            print(f"   - Propiedad: {residente.propiedad}")
            print(f"   - Rol: {residente.rol}")
        else:
            print(f"❌ Errores de validación: {serializer.errors}")
            
    except Exception as e:
        print(f"❌ Error en Test 2: {str(e)}")
    
    # Test 3: Verificar mediante API
    try:
        print("\n📝 Test 3: Verificación via API...")
        
        from rest_framework.test import APIClient
        from rest_framework.authtoken.models import Token
        from django.contrib.auth.models import User
        
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
            # ✅ Sin propiedad_id
        }
        
        response = client.post('/api/usuarios/residentes/', data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.data}")
        
        if response.status_code == 201:
            print("✅ Usuario creado exitosamente via API")
        else:
            print("❌ Error creando usuario via API")
            
    except Exception as e:
        print(f"❌ Error en Test 3: {str(e)}")
    
    print("\n🧹 Limpiando datos de prueba...")
    
    # Limpiar usuarios de prueba
    test_usernames = [
        'test_sin_propiedad', 
        'test_serializer_sin_prop',
        'test_api_sin_prop'
    ]
    
    for username in test_usernames:
        try:
            user = User.objects.get(username=username)
            user.delete()
            print(f"🗑️  Usuario {username} eliminado")
        except User.DoesNotExist:
            pass
    
    print("\n✅ Pruebas completadas!")

def mostrar_usuarios_sin_propiedad():
    """Muestra todos los usuarios que no tienen propiedad asignada"""
    
    print("\n📊 USUARIOS SIN PROPIEDAD ASIGNADA:")
    print("=" * 40)
    
    residentes_sin_propiedad = Residente.objects.filter(propiedad__isnull=True)
    
    if residentes_sin_propiedad.exists():
        for residente in residentes_sin_propiedad:
            print(f"👤 {residente.usuario.username} ({residente.rol}) - Sin propiedad")
    else:
        print("ℹ️  No hay residentes sin propiedad asignada")

if __name__ == "__main__":
    # Ejecutar pruebas
    test_usuario_sin_propiedad()
    
    # Mostrar usuarios existentes sin propiedad
    mostrar_usuarios_sin_propiedad()
    
    print("\n🎯 RESULTADO:")
    print("Si todas las pruebas son exitosas, entonces:")
    print("✅ Los usuarios pueden crearse sin propiedad asignada")
    print("✅ El campo propiedad es opcional como se solicitó")
    print("✅ No hay errores de validación")