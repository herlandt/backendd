#!/usr/bin/env python
"""
🚗 SCRIPT PARA CREAR VEHÍCULOS DE PRUEBA
Crea datos de prueba para el sistema de reconocimiento vehicular
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from seguridad.models import Vehiculo, EventoSeguridad
from condominio.models import Propiedad
from usuarios.models import User

def crear_vehiculos_prueba():
    """Crea vehículos de prueba para el simulador"""
    
    print("🚗 CREANDO VEHÍCULOS DE PRUEBA")
    print("=" * 50)
    
    # Placas que el simulador detectará
    placas_prueba = [
        ('ABC123', 'Toyota Corolla - Casa 101'),
        ('DEF456', 'Honda Civic - Casa 102'), 
        ('XYZ789', 'Chevrolet Spark - Casa 103'),
        ('LMN012', 'Nissan Sentra - Casa 104'),
        ('GHI345', 'Ford Focus - Visitante'),
        ('JKL678', 'Mazda 3 - Administración')
    ]
    
    try:
        # Obtener propiedades existentes
        propiedades = list(Propiedad.objects.all())
        
        if len(propiedades) < 4:
            print("⚠️  Creando propiedades de prueba...")
            for i in range(1, 7):
                propiedad, created = Propiedad.objects.get_or_create(
                    numero_casa=f"Casa {100 + i}",
                    defaults={
                        'tipo_vivienda': 'casa',
                        'area_m2': 120.0,
                        'habitaciones': 3,
                        'banos': 2,
                    }
                )
                if created:
                    print(f"   ✅ Creada: {propiedad.numero_casa}")
            
            propiedades = list(Propiedad.objects.all())
        
        # Limpiar vehículos existentes con estas placas
        print("\n🧹 Limpiando vehículos existentes...")
        placas_existentes = [placa for placa, _ in placas_prueba]
        deleted_count = Vehiculo.objects.filter(placa__in=placas_existentes).delete()[0]
        print(f"   🗑️  Eliminados {deleted_count} vehículos")
        
        # Crear nuevos vehículos
        print("\n🚗 Creando vehículos de prueba...")
        vehiculos_creados = 0
        
        for i, (placa, descripcion) in enumerate(placas_prueba):
            # Asignar a propiedades (primeros 4) o dejar sin asignar (visitantes/admin)
            if i < 4 and i < len(propiedades):
                propiedad = propiedades[i]
                visitante = None
            else:
                propiedad = None
                visitante = None
            
            vehiculo = Vehiculo.objects.create(
                placa=placa,
                propiedad=propiedad,
                visitante=visitante
            )
            
            vehiculos_creados += 1
            if propiedad:
                print(f"   ✅ {placa} -> {propiedad.numero_casa} ({descripcion})")
            else:
                print(f"   ✅ {placa} -> Sin asignar ({descripcion})")
        
        print(f"\n📊 RESUMEN:")
        print(f"   🚗 Vehículos creados: {vehiculos_creados}")
        print(f"   🏠 Vehículos de residentes: {Vehiculo.objects.filter(propiedad__isnull=False).count()}")
        print(f"   👥 Vehículos sin asignar: {Vehiculo.objects.filter(propiedad__isnull=True).count()}")
        
        # Mostrar resumen de vehículos autorizados
        print(f"\n🔐 VEHÍCULOS AUTORIZADOS PARA PRUEBAS:")
        for vehiculo in Vehiculo.objects.all():
            if vehiculo.propiedad:
                print(f"   ✅ {vehiculo.placa} - {vehiculo.propiedad.numero_casa}")
            else:
                print(f"   ❌ {vehiculo.placa} - Sin autorización")
        
        # Limpiar eventos anteriores
        print(f"\n🧹 Limpiando eventos anteriores...")
        eventos_deleted = EventoSeguridad.objects.all().delete()[0]
        print(f"   🗑️  Eliminados {eventos_deleted} eventos")
        
        print(f"\n🎯 CONFIGURACIÓN LISTA:")
        print(f"   📺 Ejecuta el simulador: python ia_scripts/gate_simulator.py")
        print(f"   🌐 O abre: http://localhost:8080")
        print(f"   📱 API Backend: http://127.0.0.1:8000/api/seguridad/ia/control-vehicular/")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    crear_vehiculos_prueba()