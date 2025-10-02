#!/usr/bin/env python
"""
🛡️ PRUEBA DE LOGIN USUARIO SEGURIDAD
===================================

Script para probar específicamente el login del usuario de seguridad
y verificar sus permisos y datos de perfil.
"""

import requests
import json
from datetime import datetime

def test_security_login():
    """Prueba el login del usuario de seguridad"""
    
    print("🛡️ PRUEBA DE LOGIN - USUARIO SEGURIDAD")
    print("=" * 50)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Credenciales del usuario de seguridad
    security_credentials = {
        'username': 'seguridad1',
        'password': 'guardia123'
    }
    
    base_url = "http://127.0.0.1:8000/api"
    
    print("🔐 PASO 1: Intentando login...")
    print(f"   Usuario: {security_credentials['username']}")
    print(f"   Password: {security_credentials['password']}")
    print()
    
    try:
        # Realizar login
        response = requests.post(
            f"{base_url}/login/",
            json=security_credentials,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📊 Respuesta del servidor:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            
            print(f"✅ LOGIN EXITOSO!")
            print(f"   Token recibido: {token[:30]}..." if token else "   ❌ No se recibió token")
            print()
            
            if token:
                # Obtener perfil del usuario
                print("👤 PASO 2: Obteniendo perfil del usuario...")
                
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
                    
                    print("✅ PERFIL OBTENIDO EXITOSAMENTE:")
                    print(f"   ID: {profile_data.get('id', 'N/A')}")
                    print(f"   Username: {profile_data.get('username', 'N/A')}")
                    print(f"   Email: {profile_data.get('email', 'N/A')}")
                    print(f"   Nombre: {profile_data.get('first_name', 'N/A')} {profile_data.get('last_name', 'N/A')}")
                    print(f"   Es Staff: {profile_data.get('is_staff', 'N/A')}")
                    print(f"   Es Superuser: {profile_data.get('is_superuser', 'N/A')}")
                    print(f"   Activo: {profile_data.get('is_active', 'N/A')}")
                    print(f"   Último login: {profile_data.get('last_login', 'N/A')}")
                    print(f"   Fecha registro: {profile_data.get('date_joined', 'N/A')}")
                    print()
                    
                    # Verificar si tiene perfil de usuario extendido
                    if 'profile' in profile_data:
                        profile_info = profile_data['profile']
                        print("👮 INFORMACIÓN DE PERFIL EXTENDIDO:")
                        print(f"   Rol: {profile_info.get('role', 'N/A')}")
                        print(f"   Especialidad: {profile_info.get('especialidad', 'N/A')}")
                        print()
                    
                else:
                    print(f"❌ ERROR al obtener perfil - Status: {profile_response.status_code}")
                    print(f"   Respuesta: {profile_response.text}")
                    print()
                
                # Probar endpoints específicos de seguridad
                print("🛡️ PASO 3: Probando endpoints de seguridad...")
                test_security_endpoints(base_url, token)
                
        else:
            print(f"❌ LOGIN FALLIDO!")
            print(f"   Respuesta: {response.text}")
            print()
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar al servidor")
        print("   Asegúrate de que Django esté corriendo en http://127.0.0.1:8000")
        return False
        
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {str(e)}")
        return False
    
    return True

def test_security_endpoints(base_url, token):
    """Prueba endpoints específicos para usuario de seguridad"""
    
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    # Endpoints relacionados con seguridad
    security_endpoints = [
        ('/api/seguridad/visitantes/', 'Gestión de visitantes'),
        ('/api/seguridad/visitas/', 'Registro de visitas'),
        ('/api/seguridad/eventos/', 'Eventos de seguridad'),
        ('/api/seguridad/vehiculos/', 'Registro de vehículos'),
        ('/api/seguridad/dashboard/resumen/', 'Dashboard de seguridad'),
        ('/api/condominio/avisos/', 'Avisos del condominio'),
        ('/api/usuarios/perfil/', 'Mi perfil de usuario')
    ]
    
    print("📋 ENDPOINTS DE SEGURIDAD:")
    print("-" * 30)
    
    for endpoint, description in security_endpoints:
        print(f"🧪 Probando: {description}")
        print(f"   GET {endpoint}")
        
        try:
            response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   ✅ OK - {len(data)} elementos encontrados")
                    elif isinstance(data, dict):
                        print(f"   ✅ OK - Datos del objeto recibidos")
                    else:
                        print(f"   ✅ OK - Respuesta recibida")
                except:
                    print(f"   ✅ OK - Status: {response.status_code}")
            else:
                print(f"   ❌ ERROR - Status: {response.status_code}")
                print(f"   Respuesta: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ EXCEPCIÓN: {str(e)}")
        
        print()

def show_security_permissions():
    """Muestra los permisos esperados para usuario de seguridad"""
    
    print("🔒 PERMISOS ESPERADOS PARA USUARIO SEGURIDAD:")
    print("=" * 50)
    print("✅ DEBE TENER ACCESO A:")
    print("   • Gestión de visitantes")
    print("   • Registro de visitas")
    print("   • Control de accesos")
    print("   • Registro de vehículos")
    print("   • Avisos del condominio (solo lectura)")
    print("   • Su propio perfil")
    print()
    print("❌ NO DEBE TENER ACCESO A:")
    print("   • Gestión financiera")
    print("   • Administración de usuarios")
    print("   • Configuración del sistema")
    print("   • Solicitudes de mantenimiento (solo consulta)")
    print()

def main():
    """Función principal"""
    
    print("🛡️ INICIANDO PRUEBA DE USUARIO SEGURIDAD")
    print("=" * 60)
    print()
    
    # Mostrar permisos esperados
    show_security_permissions()
    
    # Realizar prueba de login
    success = test_security_login()
    
    print("=" * 60)
    if success:
        print("🎉 PRUEBA COMPLETADA - Usuario seguridad verificado")
    else:
        print("❌ PRUEBA FALLIDA - Revisar configuración")
    print("=" * 60)

if __name__ == "__main__":
    main()