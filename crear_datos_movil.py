#!/usr/bin/env python
"""
Script para crear datos de prueba realistas para la app móvil
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from datetime import datetime, date, timedelta
from decimal import Decimal
from finanzas.models import Gasto, Multa, Pago, PagoMulta
from usuarios.models import User, Residente
from condominio.models import Propiedad

def crear_datos_prueba_movil():
    """Crea datos de prueba realistas para la app móvil"""
    
    print("📱 CREANDO DATOS DE PRUEBA PARA APP MÓVIL")
    print("=" * 60)
    
    try:
        # Verificar que existan propiedades y residentes
        propiedades = Propiedad.objects.all()
        residentes = Residente.objects.all()
        
        print(f"🏠 Propiedades disponibles: {propiedades.count()}")
        print(f"👥 Residentes disponibles: {residentes.count()}")
        
        if propiedades.count() == 0:
            print("❌ No hay propiedades. Creando algunas...")
            # Crear propiedades de ejemplo
            for i in range(1, 6):
                Propiedad.objects.get_or_create(
                    numero_casa=f"Casa {100 + i}",
                    defaults={
                        'tipo_vivienda': 'casa',
                        'area_m2': 120.0,
                        'habitaciones': 3,
                        'banos': 2,
                    }
                )
            propiedades = Propiedad.objects.all()
            print(f"✅ Creadas {propiedades.count()} propiedades")
        
        # Limpiar datos existentes de prueba
        print("\n🧹 Limpiando datos anteriores...")
        Pago.objects.all().delete()
        PagoMulta.objects.all().delete()
        Gasto.objects.all().delete()
        Multa.objects.all().delete()
        
        # Crear gastos mensuales realistas para las últimas 3 meses
        print("\n💰 Creando gastos mensuales...")
        meses_gastos = [
            (8, 2025, "Cuota de administración agosto 2025"),
            (9, 2025, "Cuota de administración septiembre 2025"),
            (10, 2025, "Cuota de administración octubre 2025"),
        ]
        
        gastos_creados = 0
        for mes, anio, descripcion in meses_gastos:
            fecha_emision = date(anio, mes, 1)
            fecha_vencimiento = fecha_emision + timedelta(days=15)
            
            for propiedad in propiedades[:4]:  # Solo para las primeras 4 propiedades
                gasto = Gasto.objects.create(
                    propiedad=propiedad,
                    monto=Decimal('150.00'),
                    fecha_emision=fecha_emision,
                    fecha_vencimiento=fecha_vencimiento,
                    descripcion=descripcion,
                    pagado=False,
                    mes=mes,
                    anio=anio
                )
                gastos_creados += 1
        
        print(f"✅ Creados {gastos_creados} gastos mensuales")
        
        # Marcar algunos gastos como pagados (crear historial)
        print("\n💳 Creando historial de pagos...")
        gastos_agosto = Gasto.objects.filter(mes=8, anio=2025)
        pagos_creados = 0
        
        for gasto in gastos_agosto[:2]:  # Pagar solo los primeros 2
            pago = Pago.objects.create(
                gasto=gasto,
                usuario=User.objects.first(),
                monto_pagado=gasto.monto,
                estado_pago='PAGADO'
            )
            gasto.pagado = True
            gasto.save()
            pagos_creados += 1
        
        print(f"✅ Creados {pagos_creados} pagos (historial)")
        
        # Crear multas realistas
        print("\n🚫 Creando multas...")
        conceptos_multas = [
            ("Ruido excesivo", 75.00, "Música a alto volumen después de las 22:00"),
            ("Mascota sin correa", 50.00, "Perro suelto en áreas comunes"),
            ("Parqueo indebido", 100.00, "Vehículo en zona no autorizada"),
            ("Basura fuera de horario", 25.00, "Sacar basura antes del horario establecido"),
        ]
        
        multas_creadas = 0
        for i, (concepto, monto, descripcion) in enumerate(conceptos_multas):
            if i < len(propiedades):
                multa = Multa.objects.create(
                    propiedad=propiedades[i],
                    concepto=concepto,
                    monto=Decimal(str(monto)),
                    fecha_emision=date.today() - timedelta(days=10 + i),
                    fecha_vencimiento=date.today() + timedelta(days=15),
                    descripcion=descripcion,
                    pagado=False,
                    mes=10,
                    anio=2025
                )
                multas_creadas += 1
        
        print(f"✅ Creadas {multas_creadas} multas")
        
        # Pagar una multa para crear historial
        print("\n💳 Creando historial de pagos de multas...")
        primera_multa = Multa.objects.first()
        if primera_multa:
            pago_multa = PagoMulta.objects.create(
                multa=primera_multa,
                usuario=User.objects.first(),
                monto_pagado=primera_multa.monto
            )
            primera_multa.pagado = True
            primera_multa.save()
            print(f"✅ Pagada 1 multa para historial")
        
        # Mostrar resumen final
        print(f"\n📊 RESUMEN DE DATOS CREADOS")
        print("-" * 60)
        
        total_gastos = Gasto.objects.count()
        gastos_pendientes = Gasto.objects.filter(pagado=False).count()
        gastos_pagados = Gasto.objects.filter(pagado=True).count()
        
        total_multas = Multa.objects.count()
        multas_pendientes = Multa.objects.filter(pagado=False).count()
        multas_pagadas = Multa.objects.filter(pagado=True).count()
        
        total_pagos = Pago.objects.count()
        total_pagos_multas = PagoMulta.objects.count()
        
        print(f"💰 Gastos totales: {total_gastos}")
        print(f"   - Pendientes: {gastos_pendientes}")
        print(f"   - Pagados: {gastos_pagados}")
        
        print(f"🚫 Multas totales: {total_multas}")
        print(f"   - Pendientes: {multas_pendientes}")
        print(f"   - Pagadas: {multas_pagadas}")
        
        print(f"💳 Historial pagos gastos: {total_pagos}")
        print(f"💳 Historial pagos multas: {total_pagos_multas}")
        
        # Información por residente
        print(f"\n👤 DATOS POR RESIDENTE")
        print("-" * 60)
        
        for residente in residentes[:3]:  # Mostrar solo los primeros 3
            if residente.propiedad:
                gastos_res = Gasto.objects.filter(propiedad=residente.propiedad)
                gastos_pend_res = gastos_res.filter(pagado=False)
                multas_res = Multa.objects.filter(propiedad=residente.propiedad)
                multas_pend_res = multas_res.filter(pagado=False)
                
                print(f"🏠 {residente.usuario.username} - {residente.propiedad.numero_casa}")
                print(f"   💰 Gastos: {gastos_res.count()} (pendientes: {gastos_pend_res.count()})")
                print(f"   🚫 Multas: {multas_res.count()} (pendientes: {multas_pend_res.count()})")
                
                if gastos_pend_res.exists():
                    total_pendiente = sum(g.monto for g in gastos_pend_res)
                    print(f"   💸 Total pendiente gastos: ${total_pendiente}")
                
                if multas_pend_res.exists():
                    total_multas_pend = sum(m.monto for m in multas_pend_res)
                    print(f"   💸 Total pendiente multas: ${total_multas_pend}")
        
        print(f"\n🎯 ENDPOINTS PARA PROBAR EN LA APP MÓVIL")
        print("-" * 60)
        print("🔗 GET /api/finanzas/gastos/mis_gastos_pendientes/")
        print("🔗 GET /api/finanzas/multas/mis_multas_pendientes/")
        print("🔗 GET /api/finanzas/pagos/ (historial)")
        print("🔗 GET /api/finanzas/pagos-multas/ (historial)")
        print("🔗 GET /api/finanzas/estado-de-cuenta/")
        
        print(f"\n✅ DATOS DE PRUEBA CREADOS EXITOSAMENTE")
        print("🎉 La app móvil ya puede probar con datos realistas!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    crear_datos_prueba_movil()