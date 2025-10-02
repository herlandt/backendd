#!/usr/bin/env python
"""
Script para crear usuarios de prueba para el sistema de condominio
Ejecutar con: python manage.py shell < crear_usuarios_prueba.py
"""

from django.contrib.auth.models import User
from usuarios.models import UserProfile, Residente
from condominio.models import Propiedad

print("🚀 Iniciando creación de usuarios de prueba...")

# Datos de usuarios para crear
users_data = [
    {
        'username': 'admin',
        'password': 'admin123', 
        'email': 'admin@condominio.com',
        'first_name': 'Administrador',
        'last_name': 'Sistema',
        'role': 'PROPIETARIO',
        'is_staff': True,
        'is_superuser': True
    },
    {
        'username': 'residente1',
        'password': 'isaelOrtiz2',
        'email': 'residente1@gmail.com', 
        'first_name': 'Juan Carlos',
        'last_name': 'Pérez',
        'role': 'RESIDENTE'
    },
    {
        'username': 'residente2',
        'password': 'maria2024',
        'email': 'maria.garcia@gmail.com',
        'first_name': 'María',
        'last_name': 'García', 
        'role': 'RESIDENTE'
    },
    {
        'username': 'seguridad1',
        'password': 'guardia123',
        'email': 'seguridad@condominio.com',
        'first_name': 'Carlos',
        'last_name': 'Guardia',
        'role': 'SEGURIDAD'
    },
    {
        'username': 'electricista1', 
        'password': 'electrico123',
        'email': 'electricista@condominio.com',
        'first_name': 'Roberto',
        'last_name': 'Electricista',
        'role': 'MANTENIMIENTO',
        'especialidad': 'ELECTRICIDAD'
    },
    {
        'username': 'plomero1',
        'password': 'plomeria123', 
        'email': 'plomero@condominio.com',
        'first_name': 'Miguel',
        'last_name': 'Plomero',
        'role': 'MANTENIMIENTO',
        'especialidad': 'PLOMERIA'
    },
    {
        'username': 'mantenimiento1',
        'password': 'general123',
        'email': 'mantenimiento@condominio.com',
        'first_name': 'Luis',
        'last_name': 'Mantenimiento', 
        'role': 'MANTENIMIENTO',
        'especialidad': 'GENERAL'
    }
]

# Crear usuarios
created_users = 0
existing_users = 0

for user_data in users_data:
    username = user_data['username']
    
    if not User.objects.filter(username=username).exists():
        try:
            # Crear usuario
            user = User.objects.create_user(
                username=username,
                password=user_data['password'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                is_staff=user_data.get('is_staff', False),
                is_superuser=user_data.get('is_superuser', False)
            )
            
            # Crear perfil de usuario
            UserProfile.objects.create(
                user=user,
                role=user_data['role'],
                especialidad=user_data.get('especialidad', '')
            )
            
            print(f"✅ Usuario {username} creado exitosamente")
            created_users += 1
            
        except Exception as e:
            print(f"❌ Error creando usuario {username}: {e}")
    else:
        print(f"⚠️ Usuario {username} ya existe")
        existing_users += 1

print(f"\n📊 RESUMEN:")
print(f"✅ Usuarios creados: {created_users}")
print(f"⚠️ Usuarios existentes: {existing_users}")
print(f"📱 Total usuarios en sistema: {User.objects.count()}")

# Crear propiedades de ejemplo si no existen
print(f"\n🏠 Creando propiedades de ejemplo...")

propiedades_data = [
    {
        'numero_casa': '101',
        'metros_cuadrados': 85.50,
        'propietario_username': 'residente1'
    },
    {
        'numero_casa': '201', 
        'metros_cuadrados': 92.00,
        'propietario_username': 'residente2'
    },
    {
        'numero_casa': '301',
        'metros_cuadrados': 110.00,
        'propietario_username': 'admin'
    }
]

created_properties = 0
for prop_data in propiedades_data:
    numero_casa = prop_data['numero_casa']
    
    if not Propiedad.objects.filter(numero_casa=numero_casa).exists():
        try:
            propietario = User.objects.get(username=prop_data['propietario_username'])
            
            propiedad = Propiedad.objects.create(
                numero_casa=numero_casa,
                propietario=propietario,
                metros_cuadrados=prop_data['metros_cuadrados']
            )
            
            print(f"✅ Propiedad {numero_casa} creada para {propietario.username}")
            created_properties += 1
            
        except User.DoesNotExist:
            print(f"❌ Propietario {prop_data['propietario_username']} no encontrado")
        except Exception as e:
            print(f"❌ Error creando propiedad {numero_casa}: {e}")
    else:
        print(f"⚠️ Propiedad {numero_casa} ya existe")

print(f"\n🏠 Propiedades creadas: {created_properties}")
print(f"🏠 Total propiedades: {Propiedad.objects.count()}")

# Asociar residentes con propiedades
print(f"\n👥 Asociando residentes con propiedades...")

try:
    # Residente1 -> Propiedad 101
    residente1 = User.objects.get(username='residente1')
    propiedad101 = Propiedad.objects.get(numero_casa='101')
    
    residente_obj1, created = Residente.objects.get_or_create(
        usuario=residente1,
        defaults={'propiedad': propiedad101, 'rol': 'propietario'}
    )
    
    if created:
        print(f"✅ Residente1 asociado con propiedad 101")
    else:
        print(f"⚠️ Residente1 ya estaba asociado")
        
    # Residente2 -> Propiedad 201
    residente2 = User.objects.get(username='residente2')
    propiedad201 = Propiedad.objects.get(numero_casa='201')
    
    residente_obj2, created = Residente.objects.get_or_create(
        usuario=residente2,
        defaults={'propiedad': propiedad201, 'rol': 'propietario'}
    )
    
    if created:
        print(f"✅ Residente2 asociado con propiedad 201")
    else:
        print(f"⚠️ Residente2 ya estaba asociado")
        
except Exception as e:
    print(f"❌ Error asociando residentes: {e}")

print(f"\n🎉 ¡Creación de usuarios de prueba completada!")
print(f"📋 Revisar archivo USUARIOS_PRUEBA_FRONTEND.md para credenciales")
print(f"🌐 Backend disponible en: http://127.0.0.1:8000/api/")
print(f"📚 Documentación en: http://127.0.0.1:8000/api/schema/swagger-ui/")