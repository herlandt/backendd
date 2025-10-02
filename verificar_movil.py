#!/usr/bin/env python
"""
Script de verificación rápida para el equipo móvil
Verifica que todos los endpoints funcionen antes de integrar
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests
import json
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

def verificacion_rapida():
    """Verificación rápida de endpoints para móvil"""
    
    print("🚀 VERIFICACIÓN RÁPIDA - ENDPOINTS MÓVIL")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # 1. Verificar que el servidor esté corriendo
    print("1. 🌐 Verificando servidor...")
    try:
        response = requests.get(f"{base_url}/api/", timeout=3)
        if response.status_code == 200:
            print("   ✅ Servidor corriendo correctamente")
        else:
            print(f"   ⚠️  Servidor responde con código {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ SERVIDOR NO DISPONIBLE - Ejecutar: python manage.py runserver")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # 2. Verificar login
    print("\n2. 🔐 Verificando autenticación...")
    try:
        user = User.objects.first()
        if not user:
            print("   ❌ No hay usuarios en el sistema")
            return False
        
        # Crear token si no existe
        token, created = Token.objects.get_or_create(user=user)
        print(f"   ✅ Usuario de prueba: {user.username}")
        print(f"   ✅ Token: {token.key[:20]}...")
        
        headers = {'Authorization': f'Token {token.key}'}
        
    except Exception as e:
        print(f"   ❌ Error en autenticación: {e}")
        return False
    
    # 3. Verificar endpoints críticos
    print("\n3. 📡 Verificando endpoints críticos...")
    
    endpoints_criticos = [
        ('/api/finanzas/gastos/mis_gastos_pendientes/', 'Gastos pendientes'),
        ('/api/finanzas/multas/mis_multas_pendientes/', 'Multas pendientes'),
        ('/api/finanzas/pagos/', 'Historial pagos'),
        ('/api/finanzas/estado-de-cuenta/', 'Estado de cuenta'),
    ]
    
    todos_ok = True
    for endpoint, descripcion in endpoints_criticos:
        try:
            response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=3)
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 'objeto'
                print(f"   ✅ {descripcion}: {count} elementos")
            else:
                print(f"   ❌ {descripcion}: Error {response.status_code}")
                todos_ok = False
        except Exception as e:
            print(f"   ❌ {descripcion}: {str(e)}")
            todos_ok = False
    
    # 4. Resumen final
    print(f"\n4. 📊 Resumen final:")
    if todos_ok:
        print("   🎉 ¡TODOS LOS ENDPOINTS FUNCIONAN CORRECTAMENTE!")
        print("   ✅ El equipo móvil puede proceder con la integración")
        print(f"\n📝 Información para el equipo móvil:")
        print(f"   🔗 Base URL: {base_url}/api/")
        print(f"   🔑 Token de prueba: {token.key}")
        print(f"   👤 Usuario de prueba: {user.username}")
        
        # Ejemplo de petición
        print(f"\n💡 Ejemplo de petición:")
        print(f"   curl -H 'Authorization: Token {token.key}' \\")
        print(f"        {base_url}/api/finanzas/gastos/mis_gastos_pendientes/")
        
        return True
    else:
        print("   ❌ HAY PROBLEMAS CON ALGUNOS ENDPOINTS")
        print("   🔧 Revisar configuración del servidor")
        return False

if __name__ == "__main__":
    verificacion_rapida()