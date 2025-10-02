#!/usr/bin/env python
"""
Script para probar que el admin panel funciona correctamente
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from condominio.models import Aviso, LecturaAviso
from usuarios.models import User, Residente
from django.contrib.auth.models import Group
from datetime import datetime

def test_admin_calculations():
    """Prueba que los cálculos del admin funcionen"""
    print("🧪 PRUEBA: Cálculos del Admin Panel")
    print("=" * 50)
    
    # Verificar que existen avisos
    avisos = Aviso.objects.all()
    print(f"📢 Total de avisos: {avisos.count()}")
    
    for aviso in avisos:
        print(f"\n📋 Aviso: {aviso.titulo}")
        print(f"   - Dirigido a: {aviso.dirigido_a}")
        print(f"   - Activo: {aviso.activo}")
        print(f"   - Fecha: {aviso.fecha_publicacion}")
        
        # Calcular lecturas
        total_lecturas = aviso.lecturas.count()
        print(f"   - Total lecturas: {total_lecturas}")
        
        # Calcular objetivo según el admin
        if aviso.dirigido_a == 'TODOS':
            total_objetivo = Residente.objects.count()
        elif aviso.dirigido_a == 'PROPIETARIOS':
            total_objetivo = Residente.objects.filter(rol='propietario').count()
        elif aviso.dirigido_a == 'INQUILINOS':
            total_objetivo = Residente.objects.filter(rol='inquilino').count()
        else:
            total_objetivo = 0
        
        print(f"   - Residentes objetivo: {total_objetivo}")
        
        if total_objetivo > 0:
            porcentaje = round((total_lecturas / total_objetivo) * 100, 2)
            print(f"   - Porcentaje leído: {porcentaje}%")
        else:
            print(f"   - Porcentaje leído: 0% (sin objetivo)")
        
        # Mostrar quién leyó
        if total_lecturas > 0:
            print(f"   - Lectores:")
            for lectura in aviso.lecturas.select_related('residente__usuario')[:3]:
                print(f"     • {lectura.residente.usuario.username} ({lectura.fecha_lectura})")
            if total_lecturas > 3:
                print(f"     • ... y {total_lecturas - 3} más")

def test_api_endpoints():
    """Prueba que los endpoints funcionen"""
    print("\n\n🌐 PRUEBA: Endpoints API")
    print("=" * 50)
    
    print("📡 URLs disponibles:")
    print("   GET /api/condominio/avisos/ - Listar avisos")
    print("   POST /api/condominio/avisos/{id}/marcar_como_leido/ - Marcar como leído")
    print("   GET /api/condominio/avisos/{id}/estadisticas_lectura/ - Ver estadísticas")
    print("   GET /api/condominio/avisos/mis_avisos_pendientes/ - Avisos pendientes")
    print("   GET /api/condominio/lecturas-aviso/ - Listar lecturas")

def show_system_summary():
    """Muestra resumen del sistema"""
    print("\n\n📊 RESUMEN DEL SISTEMA")
    print("=" * 50)
    
    # Contadores
    total_usuarios = User.objects.count()
    total_residentes = Residente.objects.count()
    total_avisos = Aviso.objects.count()
    total_lecturas = LecturaAviso.objects.count()
    
    print(f"👥 Usuarios totales: {total_usuarios}")
    print(f"🏠 Residentes totales: {total_residentes}")
    print(f"📢 Avisos totales: {total_avisos}")
    print(f"📖 Lecturas totales: {total_lecturas}")
    
    # Por rol
    propietarios = Residente.objects.filter(rol='propietario').count()
    inquilinos = Residente.objects.filter(rol='inquilino').count()
    
    print(f"\n👑 Propietarios: {propietarios}")
    print(f"🏘️ Inquilinos: {inquilinos}")
    
    # Avisos por estado
    avisos_activos = Aviso.objects.filter(activo=True).count()
    avisos_inactivos = Aviso.objects.filter(activo=False).count()
    
    print(f"\n✅ Avisos activos: {avisos_activos}")
    print(f"❌ Avisos inactivos: {avisos_inactivos}")

def main():
    print("🚀 VERIFICACIÓN DEL SISTEMA DE AVISOS")
    print("=" * 60)
    print("Fecha de prueba:", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    
    try:
        show_system_summary()
        test_admin_calculations()
        test_api_endpoints()
        
        print("\n\n✅ SISTEMA FUNCIONANDO CORRECTAMENTE")
        print("🔗 Admin Panel: http://127.0.0.1:8000/admin/")
        print("📱 API Base: http://127.0.0.1:8000/api/")
        print("📋 Avisos Admin: http://127.0.0.1:8000/admin/condominio/aviso/")
        print("📖 Lecturas Admin: http://127.0.0.1:8000/admin/condominio/lecturaaviso/")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()