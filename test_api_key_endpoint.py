#!/usr/bin/env python3
"""
🧪 PRUEBA RÁPIDA DEL ENDPOINT DE CONTROL VEHICULAR
Verifica que el endpoint funcione con la API key correcta
"""

import requests
import json

def test_control_vehicular():
    print("🧪 PROBANDO ENDPOINT DE CONTROL VEHICULAR")
    print("=" * 50)
    
    url = "http://127.0.0.1:8000/api/seguridad/ia/control-vehicular/"
    headers = {
        'X-API-KEY': 'MI_CLAVE_SUPER_SECRETA_12345',
        'Content-Type': 'application/json'
    }
    
    # Casos de prueba
    test_cases = [
        {'placa': 'ABC123', 'tipo': 'INGRESO', 'expected': 200, 'description': 'Vehículo autorizado'},
        {'placa': 'XXX999', 'tipo': 'INGRESO', 'expected': 403, 'description': 'Vehículo no registrado'},
        {'placa': '', 'tipo': 'INGRESO', 'expected': 400, 'description': 'Placa vacía'},
    ]
    
    print("🔑 Headers enviados:")
    for key, value in headers.items():
        print(f"   {key}: {value}")
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. 🚗 {test_case['description']}")
        print(f"   📡 Placa: '{test_case['placa']}' | Tipo: {test_case['tipo']}")
        
        try:
            response = requests.post(
                url, 
                json={'placa': test_case['placa'], 'tipo': test_case['tipo']},
                headers=headers,
                timeout=10
            )
            
            print(f"   📊 Status: {response.status_code} (esperado: {test_case['expected']})")
            
            if response.status_code == test_case['expected']:
                print("   ✅ ÉXITO - Status correcto")
            else:
                print("   ❌ FALLO - Status incorrecto")
            
            # Mostrar respuesta
            try:
                data = response.json()
                print(f"   📄 Respuesta: {data.get('mensaje', 'Sin mensaje')}")
                if 'error' in data:
                    print(f"   ⚠️  Error: {data['error']}")
            except:
                print(f"   📄 Respuesta: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error de conexión: {e}")
        
        print()
    
    # Prueba sin API key para verificar error 403
    print("4. 🔒 Prueba sin API key")
    try:
        response = requests.post(
            url,
            json={'placa': 'ABC123', 'tipo': 'INGRESO'},
            headers={'Content-Type': 'application/json'},  # Sin X-API-KEY
            timeout=10
        )
        print(f"   📊 Status: {response.status_code} (esperado: 403)")
        if response.status_code == 403:
            print("   ✅ ÉXITO - API key requerida funciona correctamente")
        else:
            print("   ❌ FALLO - Debería rechazar sin API key")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 CONFIGURACIÓN PARA FRONTEND:")
    print("   Asegúrate de incluir estos headers en todas las peticiones:")
    print("   X-API-KEY: MI_CLAVE_SUPER_SECRETA_12345")
    print("   Content-Type: application/json")

if __name__ == "__main__":
    test_control_vehicular()