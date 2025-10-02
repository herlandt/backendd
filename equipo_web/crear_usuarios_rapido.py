#!/usr/bin/env python
"""
🚀 SCRIPT RÁPIDO - USUARIOS DE PRUEBA FRONTEND
==============================================
Versión simplificada para el equipo frontend.

INSTRUCCIONES:
1. cd ruta/del/backend
2. python crear_usuarios_rapido.py
3. ¡Listo! Usuarios creados

CREDENCIALES CREADAS:
- admin / admin123 (Administrador)
- residente1 / isaelOrtiz2 (Residente)
- seguridad1 / guardia123 (Seguridad)
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import UserProfile

def main():
    print("🚀 Creando usuarios de prueba para frontend...")
    
    # Usuarios básicos para frontend
    users = [
        ('admin', 'admin123', 'PROPIETARIO', True, True),
        ('residente1', 'isaelOrtiz2', 'RESIDENTE', False, False),
        ('seguridad1', 'guardia123', 'SEGURIDAD', False, False),
    ]
    
    for username, password, role, is_staff, is_superuser in users:
        try:
            # Crear o actualizar usuario
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@condominio.com',
                    'first_name': username.title(),
                    'last_name': 'Test',
                    'is_staff': is_staff,
                    'is_superuser': is_superuser,
                }
            )
            
            # Establecer contraseña
            user.set_password(password)
            user.save()
            
            # Crear perfil
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={'role': role}
            )
            profile.role = role
            profile.save()
            
            status = "✅ CREADO" if created else "🔄 ACTUALIZADO"
            print(f"{status} {username} / {password} ({role})")
            
        except Exception as e:
            print(f"❌ ERROR: {username} - {e}")
    
    print("\n🎉 ¡Usuarios listos!")
    print("🔗 Probar: http://127.0.0.1:8000/api/login/")
    print("📖 Docs: http://127.0.0.1:8000/api/schema/swagger-ui/")

if __name__ == "__main__":
    main()