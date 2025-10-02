#!/usr/bin/env python
"""
🛡️ PRUEBA MEJORADA DE LOGIN USUARIO SEGURIDAD
=============================================

Script para probar específicamente el login del usuario de seguridad
con las URLs reales del backend.
"""

import requests
import json
from datetime import datetime

def test_security_login_improved():
    """Prueba mejorada del login del usuario de seguridad"""
    
    print("🛡️ PRUEBA MEJORADA - USUARIO SEGURIDAD")
    print("=" * 50)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Credenciales del usuario de seguridad
    security_credentials = {
        'username': 'seguridad1',
        'password': 'guardia123'
    }
    
    base_url = "http://127.0.0.1:8000"
    
    print("🔐 PASO 1: Intentando login...")
    print(f"   Usuario: {security_credentials['username']}")
    print(f"   Password: {security_credentials['password']}")
    print(f"   URL: {base_url}/api/login/")
    print()
    
    try:
        # Realizar login
        response = requests.post(
            f"{base_url}/api/login/",
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
            print(f"   Datos completos: {json.dumps(data, indent=2)}")
            print()
            
            if token:
                # Obtener perfil del usuario
                print("👤 PASO 2: Obteniendo perfil del usuario...")
                test_profile_endpoint(base_url, token)
                
                # Probar endpoints específicos de seguridad
                print("🛡️ PASO 3: Probando endpoints de seguridad...")
                test_security_endpoints_real(base_url, token)
                
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

def test_profile_endpoint(base_url, token):
    """Prueba el endpoint de perfil específicamente"""
    
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    # Probar diferentes URLs posibles para el perfil
    profile_urls = [
        '/api/usuarios/perfil/',
        '/api/usuarios/profile/',
        '/api/auth/user/',
        '/api/user/',
        '/api/me/'
    ]
    
    for url in profile_urls:
        print(f"🧪 Probando perfil en: {url}")
        try:
            response = requests.get(f"{base_url}{url}", headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ PERFIL ENCONTRADO!")
                print(f"   Datos: {json.dumps(data, indent=4)}")
                return data
            elif response.status_code == 404:
                print(f"   ❌ Endpoint no existe")
            else:
                print(f"   ⚠️  Status: {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("   ❌ No se encontró endpoint de perfil funcionando")
    return None

def test_security_endpoints_real(base_url, token):
    """Prueba endpoints reales de seguridad según nuestras URLs"""
    
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    # URLs reales basadas en nuestro backend
    security_endpoints = [
        ('/api/seguridad/visitantes/', 'Gestión de visitantes'),
        ('/api/seguridad/visitas/', 'Registro de visitas'),
        ('/api/seguridad/eventos/', 'Eventos de seguridad'),
        ('/api/seguridad/vehiculos/', 'Registro de vehículos'),
        ('/api/seguridad/dashboard/resumen/', 'Dashboard resumen'),
        ('/api/seguridad/visitas-abiertas/', 'Visitas abiertas'),
        ('/api/condominio/avisos/', 'Avisos del condominio'),
        ('/api/condominio/propiedades/', 'Propiedades del condominio')
    ]
    
    print("📋 ENDPOINTS REALES DE SEGURIDAD:")
    print("-" * 40)
    
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
                        if len(data) > 0:
                            print(f"   📄 Primer elemento: {json.dumps(data[0], indent=6)}")
                    elif isinstance(data, dict):
                        print(f"   ✅ OK - Datos del objeto recibidos")
                        print(f"   📄 Datos: {json.dumps(data, indent=6)}")
                    else:
                        print(f"   ✅ OK - Respuesta: {data}")
                except:
                    print(f"   ✅ OK - Status: {response.status_code} (no JSON)")
            elif response.status_code == 404:
                print(f"   ❌ Endpoint no existe (404)")
            elif response.status_code == 403:
                print(f"   🔒 Sin permisos (403)")
            elif response.status_code == 401:
                print(f"   🔐 No autorizado (401)")
            else:
                print(f"   ⚠️  Status: {response.status_code}")
                print(f"   Respuesta: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ EXCEPCIÓN: {str(e)}")
        
        print()

def verify_user_in_database():
    """Verifica que el usuario de seguridad esté correctamente creado"""
    
    print("🔍 VERIFICANDO USUARIO EN BASE DE DATOS...")
    print("-" * 40)
    
    import os
    import sys
    import django
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    try:
        from django.contrib.auth.models import User
        from usuarios.models import UserProfile
        
        # Buscar usuario seguridad1
        user = User.objects.get(username='seguridad1')
        
        print(f"✅ Usuario encontrado en DB:")
        print(f"   ID: {user.id}")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Nombre: {user.first_name} {user.last_name}")
        print(f"   Es activo: {user.is_active}")
        print(f"   Es staff: {user.is_staff}")
        print(f"   Es superuser: {user.is_superuser}")
        print(f"   Último login: {user.last_login}")
        print(f"   Fecha registro: {user.date_joined}")
        
        # Verificar contraseña
        password_ok = user.check_password('guardia123')
        print(f"   Contraseña OK: {password_ok}")
        
        # Verificar perfil extendido
        try:
            profile = user.profile
            print(f"   Perfil extendido:")
            print(f"     Rol: {profile.role}")
            print(f"     Especialidad: {profile.especialidad}")
        except:
            print(f"   ❌ Sin perfil extendido")
        
        print()
        return True
        
    except User.DoesNotExist:
        print("❌ Usuario 'seguridad1' no encontrado en la base de datos")
        return False
    except Exception as e:
        print(f"❌ Error verificando usuario: {str(e)}")
        return False

def main():
    """Función principal"""
    
    print("🛡️ INICIANDO PRUEBA MEJORADA DE USUARIO SEGURIDAD")
    print("=" * 60)
    print()
    
    # Verificar usuario en base de datos
    db_ok = verify_user_in_database()
    
    if db_ok:
        # Realizar prueba de login
        success = test_security_login_improved()
        
        print("=" * 60)
        if success:
            print("🎉 PRUEBA COMPLETADA - Usuario seguridad verificado")
        else:
            print("❌ PRUEBA FALLIDA - Revisar configuración")
        print("=" * 60)
    else:
        print("❌ No se puede continuar - Usuario no existe en DB")

if __name__ == "__main__":
    main()