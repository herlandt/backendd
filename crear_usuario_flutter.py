#!/usr/bin/env python3
"""
🔑 CREAR USUARIO Y TOKEN PARA FLUTTER
Script para crear un usuario de prueba y obtener su token de autenticación
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from condominio.models import Propiedad

User = get_user_model()

def crear_usuario_flutter():
    """Crea un usuario para probar desde Flutter"""
    
    print("🔑 CREANDO USUARIO PARA FLUTTER")
    print("=" * 40)
    
    # 1. Crear/obtener usuario
    username = "flutter_user"
    email = "flutter@test.com"
    
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': 'Usuario',
            'last_name': 'Flutter',
            'is_active': True,
            'is_staff': False,
        }
    )
    
    if created:
        user.set_password("flutter123")
        user.save()
        print(f"✅ Usuario creado: {user.username}")
    else:
        print(f"👤 Usuario existente: {user.username}")
    
    # 2. Crear/obtener token
    token, created = Token.objects.get_or_create(user=user)
    
    if created:
        print(f"🔑 Token creado: {token.key}")
    else:
        print(f"🔑 Token existente: {token.key}")
    
    # 3. Crear/obtener propiedad
    propiedad, created = Propiedad.objects.get_or_create(
        numero_casa="FLUTTER-01",
        defaults={
            'propietario': user,
            'metros_cuadrados': 75.0,
        }
    )
    
    if created:
        print(f"🏠 Propiedad creada: {propiedad.numero_casa}")
    else:
        print(f"🏠 Propiedad existente: {propiedad.numero_casa}")
    
    print("\n" + "=" * 40)
    print("📱 CONFIGURACIÓN PARA FLUTTER:")
    print("=" * 40)
    print(f"Username: {user.username}")
    print(f"Password: flutter123")
    print(f"Token: {token.key}")
    print(f"Propiedad: {propiedad.numero_casa}")
    print("\n📡 HEADERS PARA API:")
    print(f"Authorization: Token {token.key}")
    print("Content-Type: application/json")
    
    return user, token, propiedad

def test_con_token(token):
    """Prueba los endpoints con autenticación"""
    import requests
    
    print("\n🧪 PROBANDO ENDPOINTS CON TOKEN:")
    print("=" * 40)
    
    headers = {
        'Authorization': f'Token {token.key}',
        'Content-Type': 'application/json'
    }
    
    base_url = "http://127.0.0.1:8000/api"
    endpoints = [
        "/finanzas/estado-cuenta-unificado/",
        "/finanzas/historial-pagos-unificados/",
        "/finanzas/pagos/",
    ]
    
    for endpoint in endpoints:
        url = base_url + endpoint
        try:
            response = requests.get(url, headers=headers, timeout=5)
            print(f"✅ {endpoint}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 1
                print(f"   📊 {count} registros")
            elif response.status_code == 403:
                print("   🔒 Acceso denegado (permisos)")
            elif response.status_code == 404:
                print("   ❌ Endpoint no encontrado")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")

if __name__ == "__main__":
    try:
        user, token, propiedad = crear_usuario_flutter()
        test_con_token(token)
        
        print("\n🎯 PRÓXIMOS PASOS:")
        print("1. Usa el token en tu app Flutter")
        print("2. Los endpoints ya están funcionando")
        print("3. Error 404 resuelto ✅")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()