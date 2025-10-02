#!/usr/bin/env python
"""
🚀 SCRIPT DE USUARIOS DE PRUEBA PARA FRONTEND
===================================================

Este script crea usuarios de prueba para que el equipo frontend 
pueda probar todas las funcionalidades del sistema.

📋 INSTRUCCIONES PARA EL FRONTEND:
1. Asegúrate de que el backend esté corriendo
2. Navega a la carpeta del backend
3. Ejecuta: python crear_usuarios_prueba.py

✅ CREDENCIALES QUE SE CREARÁN:
- admin / admin123 (Administrador)
- residente1 / isaelOrtiz2 (Residente)
- residente2 / maria123 (Residente)  
- seguridad1 / guardia123 (Seguridad)
- electricista1 / tecnico123 (Mantenimiento)
- plomero1 / plomero123 (Mantenimiento)
- mantenimiento1 / mant123 (Mantenimiento General)

📅 Creado para: Equipo Frontend
📅 Fecha: Octubre 2, 2025
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import UserProfile
from condominio.models import Propiedad

def print_header():
    """Imprime el header del script"""
    print("=" * 60)
    print("🚀 CREADOR DE USUARIOS DE PRUEBA PARA FRONTEND")
    print("=" * 60)
    print("📅 Fecha: Octubre 2, 2025")
    print("🎯 Propósito: Crear usuarios para testing del frontend")
    print("💻 Para: Equipo Frontend Web/Móvil")
    print("=" * 60)
    print()

def create_test_users():
    """Crea todos los usuarios de prueba"""
    
    # Datos de usuarios para crear
    users_data = [
        {
            'username': 'admin',
            'password': 'admin123', 
            'email': 'admin@condominio.com',
            'first_name': 'Administrador',
            'last_name': 'Sistema',
            'role': 'PROPIETARIO',
            'especialidad': None,
            'is_staff': True,
            'is_superuser': True,
            'descripcion': 'Administrador principal con acceso completo'
        },
        {
            'username': 'residente1',
            'password': 'isaelOrtiz2',
            'email': 'residente1@gmail.com', 
            'first_name': 'Juan Carlos',
            'last_name': 'Pérez',
            'role': 'RESIDENTE',
            'especialidad': None,
            'is_staff': False,
            'is_superuser': False,
            'descripcion': 'Residente principal del apartamento 101'
        },
        {
            'username': 'residente2',
            'password': 'maria123',
            'email': 'maria.garcia@gmail.com',
            'first_name': 'María',
            'last_name': 'García', 
            'role': 'RESIDENTE',
            'especialidad': None,
            'is_staff': False,
            'is_superuser': False,
            'descripcion': 'Residente del apartamento 102'
        },
        {
            'username': 'seguridad1',
            'password': 'guardia123',
            'email': 'seguridad@condominio.com',
            'first_name': 'Carlos',
            'last_name': 'Guardia',
            'role': 'SEGURIDAD',
            'especialidad': 'GUARDIA_PRINCIPAL',
            'is_staff': False,
            'is_superuser': False,
            'descripcion': 'Personal de seguridad principal'
        },
        {
            'username': 'electricista1', 
            'password': 'tecnico123',
            'email': 'electricista@condominio.com',
            'first_name': 'Roberto',
            'last_name': 'Técnico',
            'role': 'MANTENIMIENTO',
            'especialidad': 'ELECTRICISTA',
            'is_staff': False,
            'is_superuser': False,
            'descripcion': 'Técnico electricista especializado'
        },
        {
            'username': 'plomero1',
            'password': 'plomero123', 
            'email': 'plomero@condominio.com',
            'first_name': 'Luis',
            'last_name': 'Fontanero',
            'role': 'MANTENIMIENTO',
            'especialidad': 'PLOMERO',
            'is_staff': False,
            'is_superuser': False,
            'descripcion': 'Técnico plomero especializado'
        },
        {
            'username': 'mantenimiento1',
            'password': 'mant123',
            'email': 'mantenimiento@condominio.com', 
            'first_name': 'Pedro',
            'last_name': 'General',
            'role': 'MANTENIMIENTO',
            'especialidad': 'GENERAL',
            'is_staff': False,
            'is_superuser': False,
            'descripcion': 'Personal de mantenimiento general'
        }
    ]
    
    print("👥 Creando usuarios de prueba...")
    print()
    
    created_users = []
    
    for user_data in users_data:
        try:
            # Verificar si el usuario ya existe
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_staff': user_data.get('is_staff', False),
                    'is_superuser': user_data.get('is_superuser', False),
                }
            )
            
            # Establecer contraseña (siempre, por si cambió)
            user.set_password(user_data['password'])
            user.save()
            
            # Crear o actualizar perfil
            profile, profile_created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': user_data['role'],
                    'especialidad': user_data.get('especialidad'),
                }
            )
            
            # Actualizar perfil si ya existía
            if not profile_created:
                profile.role = user_data['role']
                profile.especialidad = user_data.get('especialidad')
                profile.save()
            
            status = "✅ CREADO" if created else "🔄 ACTUALIZADO"
            print(f"{status} Usuario: {user_data['username']} / {user_data['password']}")
            print(f"   📧 Email: {user_data['email']}")
            print(f"   👤 Nombre: {user_data['first_name']} {user_data['last_name']}")
            print(f"   🏷️ Rol: {user_data['role']}")
            if user_data.get('especialidad'):
                print(f"   🔧 Especialidad: {user_data['especialidad']}")
            print(f"   📝 Descripción: {user_data['descripcion']}")
            print()
            
            created_users.append({
                'username': user_data['username'],
                'password': user_data['password'],
                'role': user_data['role'],
                'created': created
            })
            
        except Exception as e:
            print(f"❌ ERROR creando usuario {user_data['username']}: {str(e)}")
            print()
    
    return created_users

def create_sample_data():
    """Crea datos de ejemplo básicos"""
    print("🏢 Creando datos de ejemplo...")
    
    try:
        # Crear algunas propiedades de ejemplo
        propiedades_data = [
            {
                'numero_casa': '101',
                'propietario_username': 'residente1',
                'metros_cuadrados': 75.5
            },
            {
                'numero_casa': '102', 
                'propietario_username': 'residente2',
                'metros_cuadrados': 82.0
            },
            {
                'numero_casa': '201',
                'propietario_username': 'admin',
                'metros_cuadrados': 95.5
            }
        ]
        
        for prop_data in propiedades_data:
            try:
                propietario = User.objects.get(username=prop_data['propietario_username'])
                propiedad, created = Propiedad.objects.get_or_create(
                    numero_casa=prop_data['numero_casa'],
                    defaults={
                        'propietario': propietario,
                        'metros_cuadrados': prop_data['metros_cuadrados']
                    }
                )
                
                status = "✅ CREADA" if created else "🔄 YA EXISTE"
                print(f"{status} Propiedad: {prop_data['numero_casa']} - {propietario.get_full_name()}")
                
            except User.DoesNotExist:
                print(f"❌ ERROR: Usuario {prop_data['propietario_username']} no encontrado")
        
        print()
        
    except Exception as e:
        print(f"❌ ERROR creando datos de ejemplo: {str(e)}")
        print()

def print_credentials_summary(users):
    """Imprime resumen de credenciales creadas"""
    print("=" * 60)
    print("🔑 CREDENCIALES CREADAS PARA EL FRONTEND")
    print("=" * 60)
    
    print("\n📋 USUARIOS POR ROL:")
    
    # Agrupar por rol
    roles = {}
    for user in users:
        role = user['role']
        if role not in roles:
            roles[role] = []
        roles[role].append(user)
    
    role_icons = {
        'PROPIETARIO': '👨‍💼',
        'RESIDENTE': '🏠',
        'SEGURIDAD': '🛡️',
        'MANTENIMIENTO': '🔧'
    }
    
    for role, role_users in roles.items():
        icon = role_icons.get(role, '👤')
        print(f"\n{icon} {role}:")
        for user in role_users:
            status = "NUEVO" if user['created'] else "ACTUALIZADO"
            print(f"   • {user['username']} / {user['password']} ({status})")
    
    print(f"\n✅ Total usuarios: {len(users)}")

def print_testing_info():
    """Imprime información para testing"""
    print("\n" + "=" * 60)
    print("🧪 INFORMACIÓN PARA TESTING")
    print("=" * 60)
    
    print("\n🌐 ENDPOINTS PARA PROBAR:")
    print("POST /api/login/                    # Autenticación")
    print("GET  /api/usuarios/perfil/          # Perfil del usuario")
    print("GET  /api/propiedades/              # Lista propiedades")
    print("GET  /api/usuarios/                 # Lista usuarios (admin)")
    print("GET  /api/avisos/                   # Lista avisos")
    print("GET  /api/pagos/                    # Lista pagos")
    print("GET  /api/gastos/                   # Lista gastos")
    
    print("\n📱 EJEMPLO DE LOGIN:")
    print('curl -X POST http://127.0.0.1:8000/api/login/ \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"username":"admin","password":"admin123"}\'')
    
    print("\n🔗 DOCUMENTACIÓN:")
    print("Swagger UI: http://127.0.0.1:8000/api/schema/swagger-ui/")
    print("ReDoc:      http://127.0.0.1:8000/api/schema/redoc/")

def main():
    """Función principal"""
    try:
        print_header()
        
        # Crear usuarios
        users = create_test_users()
        
        # Crear datos de ejemplo
        create_sample_data()
        
        # Mostrar resumen
        print_credentials_summary(users)
        
        # Mostrar info de testing
        print_testing_info()
        
        print("\n" + "=" * 60)
        print("🎉 ¡USUARIOS DE PRUEBA CREADOS EXITOSAMENTE!")
        print("=" * 60)
        print("📋 El frontend ya puede usar estas credenciales para probar")
        print("🚀 Backend funcionando en: http://127.0.0.1:8000")
        print("📖 Documentación en: http://127.0.0.1:8000/api/schema/swagger-ui/")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {str(e)}")
        print("🔍 Verifica que:")
        print("   • El servidor Django esté corriendo")
        print("   • Las migraciones estén aplicadas")
        print("   • La base de datos esté accesible")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Script ejecutado exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Script terminó con errores")
        sys.exit(1)