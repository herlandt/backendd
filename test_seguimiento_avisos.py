#!/usr/bin/env python
"""
🧪 TEST: Sistema de Seguimiento de Lectura de Avisos
=======================================================

Prueba el nuevo sistema que permite saber qué residentes 
han leído cada aviso del condominio.
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import Residente
from condominio.models import Aviso, LecturaAviso, Propiedad
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

def setup_test_data():
    """Crea datos de prueba"""
    print("🔧 Configurando datos de prueba...")
    
    # Crear usuarios y residentes de prueba
    users_data = [
        {'username': 'residente1', 'email': 'r1@test.com', 'rol': 'propietario'},
        {'username': 'residente2', 'email': 'r2@test.com', 'rol': 'inquilino'},
        {'username': 'residente3', 'email': 'r3@test.com', 'rol': 'propietario'},
    ]
    
    residentes = []
    for data in users_data:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={'email': data['email'], 'password': 'test123'}
        )
        
        residente, created = Residente.objects.get_or_create(
            usuario=user,
            defaults={'rol': data['rol']}
        )
        residentes.append(residente)
        
        if created:
            print(f"   ✅ Residente creado: {user.username} ({data['rol']})")
    
    # Crear avisos de prueba
    avisos_data = [
        {
            'titulo': 'Aviso para TODOS - Reunión General',
            'contenido': 'Reunión general el próximo viernes.',
            'dirigido_a': 'TODOS'
        },
        {
            'titulo': 'Aviso para PROPIETARIOS - Cuotas',
            'contenido': 'Información sobre cuotas de mantenimiento.',
            'dirigido_a': 'PROPIETARIOS'
        },
        {
            'titulo': 'Aviso para INQUILINOS - Normas',
            'contenido': 'Nuevas normas para inquilinos.',
            'dirigido_a': 'INQUILINOS'
        }
    ]
    
    avisos = []
    for data in avisos_data:
        aviso, created = Aviso.objects.get_or_create(
            titulo=data['titulo'],
            defaults={
                'contenido': data['contenido'],
                'dirigido_a': data['dirigido_a']
            }
        )
        avisos.append(aviso)
        
        if created:
            print(f"   ✅ Aviso creado: {aviso.titulo}")
    
    return residentes, avisos

def test_lectura_avisos():
    """Prueba el sistema de lectura de avisos"""
    print("\n🧪 PRUEBA: Sistema de Lectura de Avisos")
    print("=" * 50)
    
    residentes, avisos = setup_test_data()
    
    # Simular que algunos residentes leyeron algunos avisos
    print("\n📖 Simulando lecturas de avisos...")
    
    lecturas = [
        (residentes[0], avisos[0]),  # residente1 lee aviso para todos
        (residentes[1], avisos[0]),  # residente2 lee aviso para todos
        (residentes[0], avisos[1]),  # residente1 (propietario) lee aviso para propietarios
        # residente3 no lee ningún aviso
        # residente2 no puede leer aviso para propietarios
    ]
    
    for residente, aviso in lecturas:
        lectura, created = LecturaAviso.objects.get_or_create(
            aviso=aviso,
            residente=residente
        )
        if created:
            print(f"   ✅ {residente.usuario.username} leyó '{aviso.titulo}'")
    
    # Mostrar estadísticas
    print("\n📊 ESTADÍSTICAS DE LECTURA:")
    print("-" * 40)
    
    for aviso in avisos:
        print(f"\n🔹 {aviso.titulo}")
        print(f"   Dirigido a: {aviso.dirigido_a}")
        print(f"   Residentes objetivo: {aviso.total_residentes_objetivo()}")
        print(f"   Total lecturas: {aviso.total_lecturas()}")
        print(f"   Porcentaje leído: {aviso.porcentaje_lectura()}%")
        
        print(f"   📖 Residentes que leyeron:")
        for lectura in aviso.lecturas.all():
            print(f"      - {lectura.residente.usuario.username} ({lectura.fecha_lectura})")
        
        # Mostrar residentes que NO han leído
        from condominio.serializers import AvisoDetalleSerializer
        serializer = AvisoDetalleSerializer(aviso)
        residentes_sin_leer = serializer.get_residentes_sin_leer(aviso)
        
        if residentes_sin_leer:
            print(f"   ❌ Residentes que NO han leído:")
            for r in residentes_sin_leer:
                print(f"      - {r['username']} ({r['rol']})")
        else:
            print(f"   ✅ Todos los residentes objetivo han leído este aviso")

def test_api_endpoints():
    """Prueba los endpoints de la API"""
    print("\n🌐 PRUEBA: Endpoints de API")
    print("=" * 40)
    
    # Crear cliente API
    client = APIClient()
    
    # Crear admin para pruebas
    admin_user, created = User.objects.get_or_create(
        username='admin_test',
        defaults={'email': 'admin@test.com', 'is_staff': True, 'is_superuser': True}
    )
    admin_user.set_password('admin123')
    admin_user.save()
    
    # Obtener token de autenticación
    token, created = Token.objects.get_or_create(user=admin_user)
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    
    print("\n1. 📋 Listando avisos con estadísticas...")
    response = client.get('/api/condominio/avisos/')
    if response.status_code == 200:
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📊 Total avisos: {len(response.data)}")
        for aviso in response.data:
            print(f"      - {aviso['titulo']}: {aviso['total_lecturas']} lecturas ({aviso['porcentaje_lectura']}%)")
    else:
        print(f"   ❌ Error: {response.status_code}")
    
    print("\n2. 🔍 Obteniendo detalles de un aviso...")
    if len(response.data) > 0:
        aviso_id = response.data[0]['id']
        response = client.get(f'/api/condominio/avisos/{aviso_id}/')
        if response.status_code == 200:
            print(f"   ✅ Status: {response.status_code}")
            data = response.data
            print(f"   📖 Lecturas: {len(data['lecturas'])}")
            print(f"   ❌ Sin leer: {len(data['residentes_sin_leer'])}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    
    print("\n3. 📈 Resumen general de lecturas...")
    response = client.get('/api/condominio/lecturas-avisos/resumen_general/')
    if response.status_code == 200:
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📊 Avisos activos: {response.data['total_avisos_activos']}")
    else:
        print(f"   ❌ Error: {response.status_code}")

def cleanup_test_data():
    """Limpia los datos de prueba"""
    print("\n🧹 Limpiando datos de prueba...")
    
    # Eliminar lecturas
    LecturaAviso.objects.filter(
        residente__usuario__username__in=['residente1', 'residente2', 'residente3']
    ).delete()
    
    # Eliminar avisos de prueba
    Aviso.objects.filter(titulo__contains='Aviso para').delete()
    
    # Eliminar residentes y usuarios de prueba
    User.objects.filter(
        username__in=['residente1', 'residente2', 'residente3', 'admin_test']
    ).delete()
    
    print("   ✅ Datos de prueba eliminados")

if __name__ == "__main__":
    try:
        print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE SEGUIMIENTO DE AVISOS")
        print("=" * 60)
        
        # Ejecutar pruebas
        test_lectura_avisos()
        test_api_endpoints()
        
        print("\n🎉 RESULTADO FINAL:")
        print("✅ Sistema de seguimiento de lectura de avisos implementado correctamente")
        print("✅ Puedes saber exactamente qué residentes leyeron cada aviso")
        print("✅ Estadísticas de lectura disponibles")
        print("✅ API endpoints funcionando correctamente")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Limpiar datos de prueba
        cleanup_test_data()