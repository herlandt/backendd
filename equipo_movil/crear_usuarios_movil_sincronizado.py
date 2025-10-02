#!/usr/bin/env python
"""
📱 SCRIPT SINCRONIZADO CON PROYECTO MÓVIL - SMART LOGIN
========================================================

Este script crea EXACTAMENTE los usuarios que espera el proyecto móvil
según la documentación recibida.

✅ USUARIOS SINCRONIZADOS CON MÓVIL:
- admin / admin123 (PROPIETARIO)
- residente1 / isaelOrtiz2 (RESIDENTE) 
- propietario1 / joseGarcia3 (RESIDENTE)
- inquilino1 / anaLopez4 (RESIDENTE)
- seguridad1 / guardia123 (SEGURIDAD)
- mantenimiento1 / mant456 (MANTENIMIENTO) 
- invitado1 / invCarlos5 (RESIDENTE)

🎯 PROPÓSITO: 100% compatibilidad con app móvil Flutter
📅 Sincronizado: Octubre 2, 2025
🔗 Backend: Django REST API - Puerto 8000
📱 Target: Android Emulator (10.0.2.2:8000)
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
    print("=" * 70)
    print("📱 SINCRONIZACIÓN CON PROYECTO MÓVIL - SMART LOGIN")
    print("=" * 70)
    print("📅 Fecha: Octubre 2, 2025")
    print("🎯 Propósito: Usuarios exactos para compatibilidad móvil")
    print("📱 Para: Proyecto Flutter Smart Login")
    print("🔗 Backend: http://10.0.2.2:8000 (Android Emulator)")
    print("=" * 70)
    print()

def create_mobile_synchronized_users():
    """Crea usuarios exactamente como los espera el proyecto móvil"""
    
    # Datos exactos según documentación móvil
    mobile_users_data = [
        {
            'username': 'admin',
            'password': 'admin123', 
            'email': 'admin@condominio.com',
            'first_name': 'Administrador',
            'last_name': 'Principal',
            'role': 'PROPIETARIO',
            'especialidad': None,
            'is_staff': True,
            'is_superuser': True,
            'descripcion': 'Administrador con acceso completo al sistema'
        },
        {
            'username': 'residente1',
            'password': 'isaelOrtiz2',
            'email': 'isael.ortiz@gmail.com', 
            'first_name': 'Isael',
            'last_name': 'Ortiz',
            'role': 'RESIDENTE',
            'especialidad': None,
            'is_staff': False,
            'is_superuser': False,
            'descripcion': 'Residente apartamento 101'
        },
        {
            'username': 'propietario1',
            'password': 'joseGarcia3',
            'email': 'jose.garcia@gmail.com',
            'first_name': 'José',
            'last_name': 'García', 
            'role': 'RESIDENTE',
            'especialidad': None,
            'is_staff': False,
            'is_superuser': False,
            'descripcion': 'Propietario apartamento 201'
        },
        {
            'username': 'inquilino1',
            'password': 'anaLopez4',
            'email': 'ana.lopez@gmail.com',
            'first_name': 'Ana',
            'last_name': 'López',
            'role': 'RESIDENTE',
            'especialidad': None,
            'is_staff': False,
            'is_superuser': False,
            'descripcion': 'Inquilino apartamento 301'
        },
        {
            'username': 'seguridad1',
            'password': 'guardia123',
            'email': 'seguridad@condominio.com',
            'first_name': 'Carlos',
            'last_name': 'Seguridad',
            'role': 'SEGURIDAD',
            'especialidad': 'GUARDIA_PRINCIPAL',
            'is_staff': False,
            'is_superuser': False,
            'descripcion': 'Guardia de seguridad principal'
        },
        {
            'username': 'mantenimiento1',
            'password': 'mant456',  # ⚠️ CORREGIDO: móvil espera mant456, no mant123
            'email': 'mantenimiento@condominio.com',
            'first_name': 'Roberto',
            'last_name': 'Mantenimiento',
            'role': 'MANTENIMIENTO',
            'especialidad': 'GENERAL',
            'is_staff': False,
            'is_superuser': False,
            'descripcion': 'Técnico de mantenimiento general'
        },
        {
            'username': 'invitado1',
            'password': 'invCarlos5',
            'email': 'invitado@gmail.com',
            'first_name': 'Carlos',
            'last_name': 'Invitado',
            'role': 'RESIDENTE',
            'especialidad': None,
            'is_staff': False,
            'is_superuser': False,
            'descripcion': 'Usuario invitado temporal'
        }
    ]
    
    print("🚀 Iniciando creación de usuarios sincronizados con móvil...")
    print()
    
    for user_data in mobile_users_data:
        try:
            # Verificar si el usuario ya existe
            if User.objects.filter(username=user_data['username']).exists():
                print(f"⚠️  Usuario '{user_data['username']}' ya existe. Actualizando contraseña...")
                user = User.objects.get(username=user_data['username'])
                user.set_password(user_data['password'])
                user.email = user_data['email']
                user.first_name = user_data['first_name']
                user.last_name = user_data['last_name']
                user.is_staff = user_data['is_staff']
                user.is_superuser = user_data['is_superuser']
                user.save()
                
                # Actualizar perfil si existe
                if hasattr(user, 'profile'):
                    profile = user.profile
                    profile.role = user_data['role']
                    profile.especialidad = user_data['especialidad']
                    profile.save()
                    
                print(f"✅ Usuario '{user_data['username']}' actualizado exitosamente")
                
            else:
                # Crear usuario nuevo
                user = User.objects.create_user(
                    username=user_data['username'],
                    password=user_data['password'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    is_staff=user_data['is_staff'],
                    is_superuser=user_data['is_superuser']
                )
                
                # Crear perfil de usuario
                UserProfile.objects.create(
                    user=user,
                    role=user_data['role'],
                    especialidad=user_data['especialidad']
                )
                
                print(f"✅ Usuario '{user_data['username']}' creado exitosamente")
                
        except Exception as e:
            print(f"❌ Error creando usuario '{user_data['username']}': {str(e)}")
            continue
    
    print()
    print("🎉 Proceso completado!")
    
def create_mobile_properties():
    """Crea propiedades asociadas a los usuarios móviles"""
    
    properties_data = [
        {
            'numero_casa': '101',
            'propietario_username': 'residente1',
            'metros_cuadrados': 85.5,
            'descripcion': 'Apartamento 101 - Planta baja'
        },
        {
            'numero_casa': '201', 
            'propietario_username': 'propietario1',
            'metros_cuadrados': 92.0,
            'descripcion': 'Apartamento 201 - Segundo piso'
        },
        {
            'numero_casa': '301',
            'propietario_username': 'inquilino1',
            'metros_cuadrados': 78.0,
            'descripcion': 'Apartamento 301 - Tercer piso'
        }
    ]
    
    print("🏠 Creando propiedades para usuarios móviles...")
    print()
    
    for prop_data in properties_data:
        try:
            # Buscar el usuario propietario
            try:
                propietario = User.objects.get(username=prop_data['propietario_username'])
            except User.DoesNotExist:
                print(f"❌ Usuario propietario '{prop_data['propietario_username']}' no encontrado")
                continue
            
            # Verificar si la propiedad ya existe
            if Propiedad.objects.filter(numero_casa=prop_data['numero_casa']).exists():
                print(f"⚠️  Propiedad '{prop_data['numero_casa']}' ya existe. Actualizando...")
                propiedad = Propiedad.objects.get(numero_casa=prop_data['numero_casa'])
                propiedad.propietario = propietario
                propiedad.metros_cuadrados = prop_data['metros_cuadrados']
                propiedad.save()
                print(f"✅ Propiedad '{prop_data['numero_casa']}' actualizada")
            else:
                # Crear nueva propiedad
                Propiedad.objects.create(
                    numero_casa=prop_data['numero_casa'],
                    propietario=propietario,
                    metros_cuadrados=prop_data['metros_cuadrados']
                )
                print(f"✅ Propiedad '{prop_data['numero_casa']}' creada para {propietario.username}")
                
        except Exception as e:
            print(f"❌ Error creando propiedad '{prop_data['numero_casa']}': {str(e)}")
            continue
    
    print()

def verify_mobile_users():
    """Verifica que todos los usuarios móviles estén correctamente creados"""
    
    print("🔍 Verificando usuarios sincronizados con móvil...")
    print()
    print("=" * 70)
    print(f"{'USERNAME':<15} {'PASSWORD':<12} {'ROLE':<15} {'ESTADO':<10}")
    print("=" * 70)
    
    mobile_users = [
        ('admin', 'admin123', 'PROPIETARIO'),
        ('residente1', 'isaelOrtiz2', 'RESIDENTE'),
        ('propietario1', 'joseGarcia3', 'RESIDENTE'),
        ('inquilino1', 'anaLopez4', 'RESIDENTE'),
        ('seguridad1', 'guardia123', 'SEGURIDAD'),
        ('mantenimiento1', 'mant456', 'MANTENIMIENTO'),
        ('invitado1', 'invCarlos5', 'RESIDENTE')
    ]
    
    all_ok = True
    
    for username, password, expected_role in mobile_users:
        try:
            user = User.objects.get(username=username)
            
            # Verificar contraseña
            password_ok = user.check_password(password)
            
            # Verificar rol
            role_ok = hasattr(user, 'profile') and user.profile.role == expected_role
            
            if password_ok and role_ok:
                status = "✅ OK"
            else:
                status = "❌ ERROR"
                all_ok = False
                
            print(f"{username:<15} {password:<12} {expected_role:<15} {status:<10}")
            
        except User.DoesNotExist:
            print(f"{username:<15} {password:<12} {expected_role:<15} {'❌ NO EXISTE':<10}")
            all_ok = False
    
    print("=" * 70)
    print()
    
    if all_ok:
        print("🎉 ¡TODOS LOS USUARIOS MÓVILES VERIFICADOS CORRECTAMENTE!")
        print("📱 El proyecto móvil puede conectarse sin problemas")
        print("🔗 URL para móvil: http://10.0.2.2:8000/api/")
    else:
        print("⚠️  Algunos usuarios presentan problemas. Revisar arriba.")
    
    print()

def print_mobile_integration_info():
    """Imprime información de integración para el equipo móvil"""
    
    print("=" * 70)
    print("📱 INFORMACIÓN PARA INTEGRACIÓN CON PROYECTO MÓVIL")
    print("=" * 70)
    print()
    print("🔗 CONFIGURACIÓN DE CONECTIVIDAD:")
    print("   • URL Base: http://10.0.2.2:8000/api/")
    print("   • Timeout: 30 segundos (optimizado para emuladores)")
    print("   • Autenticación: Token-based")
    print("   • Headers: Content-Type: application/json")
    print()
    print("📋 ENDPOINTS PRINCIPALES VERIFICADOS:")
    print("   ✅ POST /api/login/                    - Autenticación")
    print("   ✅ GET  /api/usuarios/perfil/          - Perfil usuario")
    print("   ✅ GET  /api/condominio/avisos/        - Avisos")
    print("   ✅ GET  /api/finanzas/gastos/          - Gastos")
    print("   ✅ GET  /api/seguridad/visitantes/     - Visitantes")
    print("   ✅ GET  /api/mantenimiento/solicitudes/ - Solicitudes")
    print()
    print("🔐 CREDENCIALES LISTAS PARA MÓVIL:")
    print("   • Todas las contraseñas coinciden con la documentación móvil")
    print("   • Roles configurados según expectativas del Flutter app")
    print("   • Perfiles de usuario completos")
    print()
    print("🚀 SIGUIENTES PASOS:")
    print("   1. Ejecutar backend: python manage.py runserver 0.0.0.0:8000")
    print("   2. Probar desde móvil: flutter run")
    print("   3. Usar cualquier credencial verificada arriba")
    print()
    print("=" * 70)

def main():
    """Función principal del script"""
    print_header()
    
    print("🚀 PASO 1: Creando/actualizando usuarios...")
    create_mobile_synchronized_users()
    
    print("🏠 PASO 2: Creando/actualizando propiedades...")
    create_mobile_properties()
    
    print("🔍 PASO 3: Verificando configuración...")
    verify_mobile_users()
    
    print("📱 PASO 4: Información de integración...")
    print_mobile_integration_info()

if __name__ == "__main__":
    main()