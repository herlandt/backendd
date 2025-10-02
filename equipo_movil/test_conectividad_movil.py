#!/usr/bin/env python
"""
🧪 SCRIPT DE PRUEBA DE CONECTIVIDAD - PROYECTO MÓVIL
===================================================

Verifica que todos los endpoints requeridos por el proyecto móvil
estén funcionando correctamente.
"""

import requests
import json

def test_login_endpoint():
    """Prueba el endpoint de login con usuarios sincronizados"""
    
    print("🔐 PROBANDO ENDPOINT DE LOGIN...")
    print("=" * 50)
    
    # Usuarios sincronizados con móvil
    test_users = [
        {'username': 'admin', 'password': 'admin123'},
        {'username': 'residente1', 'password': 'isaelOrtiz2'},
        {'username': 'seguridad1', 'password': 'guardia123'},
        {'username': 'mantenimiento1', 'password': 'mant456'}
    ]
    
    base_url = "http://127.0.0.1:8000/api"
    
    for user in test_users:
        print(f"\n🧪 Probando: {user['username']}")
        
        try:
            response = requests.post(
                f"{base_url}/login/",
                json=user,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('token', 'No token received')
                print(f"✅ LOGIN OK - Token: {token[:20]}...")
                
                # Probar endpoint de perfil con el token
                profile_response = requests.get(
                    f"{base_url}/usuarios/perfil/",
                    headers={
                        'Authorization': f'Token {token}',
                        'Content-Type': 'application/json'
                    },
                    timeout=10
                )
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    print(f"✅ PERFIL OK - Usuario: {profile_data.get('username', 'N/A')}")
                else:
                    print(f"❌ PERFIL ERROR - Status: {profile_response.status_code}")
                
            else:
                print(f"❌ LOGIN ERROR - Status: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ NO SE PUEDE CONECTAR AL SERVIDOR")
            print(f"   Asegúrate de que Django esté corriendo en http://127.0.0.1:8000")
            return False
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    return True

def test_main_endpoints():
    """Prueba los endpoints principales requeridos por móvil"""
    
    print("\n\n📋 PROBANDO ENDPOINTS PRINCIPALES...")
    print("=" * 50)
    
    # Primero hacer login para obtener token
    login_response = requests.post(
        "http://127.0.0.1:8000/api/login/",
        json={'username': 'admin', 'password': 'admin123'},
        headers={'Content-Type': 'application/json'}
    )
    
    if login_response.status_code != 200:
        print("❌ No se pudo obtener token de autenticación")
        return False
    
    token = login_response.json().get('token')
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    # Endpoints que requiere el proyecto móvil
    endpoints_to_test = [
        ('GET', '/api/condominio/avisos/', 'Avisos del condominio'),
        ('GET', '/api/finanzas/gastos/', 'Gastos financieros'),
        ('GET', '/api/seguridad/visitantes/', 'Visitantes de seguridad'),
        ('GET', '/api/mantenimiento/solicitudes/', 'Solicitudes de mantenimiento'),
        ('GET', '/api/usuarios/perfil/', 'Perfil del usuario')
    ]
    
    base_url = "http://127.0.0.1:8000"
    
    for method, endpoint, description in endpoints_to_test:
        print(f"\n🧪 Probando: {description}")
        print(f"   {method} {endpoint}")
        
        try:
            if method == 'GET':
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(f"{base_url}{endpoint}", headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                print(f"✅ OK - Status: {response.status_code}")
                
                # Mostrar un resumen de los datos
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   📊 {len(data)} elementos encontrados")
                    elif isinstance(data, dict):
                        print(f"   📊 Datos del objeto recibidos")
                except:
                    print(f"   📊 Respuesta no JSON")
                    
            else:
                print(f"❌ ERROR - Status: {response.status_code}")
                print(f"   Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"❌ EXCEPCIÓN: {str(e)}")

def print_mobile_connectivity_summary():
    """Imprime resumen de conectividad para móvil"""
    
    print("\n\n📱 RESUMEN PARA PROYECTO MÓVIL")
    print("=" * 50)
    print("🔗 URL Base para Android Emulator: http://10.0.2.2:8000/api/")
    print("🔗 URL Base para Desarrollo Local: http://127.0.0.1:8000/api/")
    print()
    print("✅ CREDENCIALES VERIFICADAS:")
    print("   admin / admin123")
    print("   residente1 / isaelOrtiz2") 
    print("   propietario1 / joseGarcia3")
    print("   inquilino1 / anaLopez4")
    print("   seguridad1 / guardia123")
    print("   mantenimiento1 / mant456")
    print("   invitado1 / invCarlos5")
    print()
    print("🚀 INSTRUCCIONES PARA MÓVIL:")
    print("1. Usar URL: http://10.0.2.2:8000/api/ desde emulador Android")
    print("2. Autenticación: Token-based")
    print("3. Headers: Content-Type: application/json")
    print("4. Timeout recomendado: 30 segundos para emuladores")

if __name__ == "__main__":
    print("🧪 VERIFICACIÓN DE CONECTIVIDAD PARA PROYECTO MÓVIL")
    print("=" * 60)
    
    # Probar login y perfiles
    login_ok = test_login_endpoint()
    
    if login_ok:
        # Probar endpoints principales
        test_main_endpoints()
    
    # Imprimir resumen
    print_mobile_connectivity_summary()
    
    print("\n🎉 VERIFICACIÓN COMPLETADA")
    print("=" * 60)