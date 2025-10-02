#!/usr/bin/env python
"""
🧪 PRUEBA DEL SISTEMA DE RECONOCIMIENTO VEHICULAR
Verifica que todos los componentes funcionen antes de usar el simulador
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests
import json
from seguridad.models import Vehiculo, EventoSeguridad

def probar_api_control_vehicular():
    """Prueba el endpoint de control vehicular"""
    
    print("🧪 PRUEBA DEL SISTEMA DE RECONOCIMIENTO VEHICULAR")
    print("=" * 60)
    
    # Configuración
    api_url = "http://127.0.0.1:8000/api/seguridad/ia/control-vehicular/"
    api_key = "MI_CLAVE_SUPER_SECRETA_12345"
    
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    # Casos de prueba
    casos_prueba = [
        {"placa": "ABC123", "tipo": "INGRESO", "esperado": 200, "descripcion": "Vehículo autorizado"},
        {"placa": "DEF456", "tipo": "INGRESO", "esperado": 200, "descripcion": "Vehículo autorizado"},
        {"placa": "GHI345", "tipo": "INGRESO", "esperado": 403, "descripcion": "Vehículo sin asignar"},
        {"placa": "XXX999", "tipo": "INGRESO", "esperado": 403, "descripcion": "Vehículo no registrado"},
        {"placa": "ABC123", "tipo": "SALIDA", "esperado": 200, "descripcion": "Salida vehículo autorizado"},
    ]
    
    print("🔍 VERIFICANDO DATOS EN BASE DE DATOS...")
    vehiculos = Vehiculo.objects.all()
    print(f"   📊 Total vehículos registrados: {vehiculos.count()}")
    
    for vehiculo in vehiculos:
        if vehiculo.propiedad:
            print(f"   ✅ {vehiculo.placa} -> {vehiculo.propiedad.numero_casa}")
        else:
            print(f"   ❌ {vehiculo.placa} -> Sin asignar")
    
    print(f"\n🌐 PROBANDO ENDPOINT: {api_url}")
    print("-" * 60)
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n{i}. 🚗 Probando: {caso['descripcion']}")
        print(f"   📡 Placa: {caso['placa']} | Tipo: {caso['tipo']}")
        
        try:
            response = requests.post(api_url, json=caso, headers=headers, timeout=5)
            
            print(f"   📊 Status Code: {response.status_code} (esperado: {caso['esperado']})")
            
            if response.status_code == caso['esperado']:
                print(f"   ✅ ÉXITO - Respuesta correcta")
            else:
                print(f"   ❌ FALLO - Respuesta inesperada")
            
            # Mostrar respuesta
            try:
                data = response.json()
                print(f"   📄 Respuesta:")
                if response.status_code in [200, 403]:
                    if 'mensaje' in data:
                        print(f"      {data['mensaje']}")
                    if 'vehiculo' in data:
                        vehiculo_info = data['vehiculo']
                        print(f"      Tipo: {vehiculo_info.get('tipo', 'N/A')}")
                        if 'propiedad' in vehiculo_info:
                            print(f"      Propiedad: {vehiculo_info['propiedad']}")
                    print(f"      Evento ID: {data.get('evento_id', 'N/A')}")
                else:
                    print(f"      Error: {data.get('error', 'Sin información')}")
            except:
                print(f"   📄 Respuesta (texto): {response.text[:100]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ ERROR: No se pudo conectar al servidor")
            print(f"   💡 Asegúrate de que Django esté corriendo: python manage.py runserver")
            return False
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print(f"\n📊 VERIFICANDO EVENTOS REGISTRADOS...")
    eventos = EventoSeguridad.objects.order_by('-fecha_hora')[:5]
    print(f"   📋 Eventos recientes: {eventos.count()}")
    
    for evento in eventos:
        print(f"   📝 {evento.placa_detectada} - {evento.accion} - {evento.fecha_hora.strftime('%H:%M:%S')}")
    
    print(f"\n🎯 PROBANDO DASHBOARD...")
    dashboard_url = "http://127.0.0.1:8000/api/seguridad/gate/dashboard/"
    
    try:
        # Necesitamos un token para el dashboard
        from django.contrib.auth.models import User
        from rest_framework.authtoken.models import Token
        
        user = User.objects.first()
        if user:
            token, created = Token.objects.get_or_create(user=user)
            dashboard_headers = {
                'Authorization': f'Token {token.key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(dashboard_url, headers=dashboard_headers, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ Dashboard funcionando correctamente")
                data = response.json()
                stats = data.get('estadisticas_hoy', {})
                print(f"   📊 Eventos hoy: {stats.get('total_eventos', 0)}")
                print(f"   ✅ Permitidos: {stats.get('accesos_permitidos', 0)}")
                print(f"   ❌ Denegados: {stats.get('accesos_denegados', 0)}")
            else:
                print(f"   ⚠️  Dashboard responde con código {response.status_code}")
        else:
            print(f"   ⚠️  No hay usuarios para probar dashboard")
    except Exception as e:
        print(f"   ❌ Error en dashboard: {e}")
    
    print(f"\n✅ SISTEMA LISTO PARA USAR")
    print("=" * 60)
    print("🎮 INSTRUCCIONES PARA USAR EL SIMULADOR:")
    print("   1. Mantén el servidor Django corriendo")
    print("   2. Ejecuta: cd ia_scripts && python gate_simulator.py")
    print("   3. Abre http://localhost:8080 en tu navegador")
    print("   4. Haz clic en 'Iniciar Simulación'")
    print("   5. Observa como se detectan las placas automáticamente")
    print("")
    print("🔗 URLs importantes:")
    print(f"   📱 API Control: {api_url}")
    print(f"   📊 Dashboard: {dashboard_url}")
    print(f"   🌐 Simulador Web: http://localhost:8080")
    
    return True

if __name__ == "__main__":
    probar_api_control_vehicular()