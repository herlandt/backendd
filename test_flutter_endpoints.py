#!/usr/bin/env python3
"""
🧪 PRUEBA DE ENDPOINTS FLUTTER
Verifica que los endpoints que busca Flutter estén funcionando
"""

import requests
import json

# Configuración
BASE_URL = "http://127.0.0.1:8000/api"

def test_endpoint(url, nombre):
    """Prueba un endpoint y muestra el resultado"""
    print(f"\n🔍 Probando: {nombre}")
    print(f"   URL: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"   ✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Datos: {len(data) if isinstance(data, list) else 'Objeto'}")
        elif response.status_code == 401:
            print("   🔒 Requiere autenticación")
        elif response.status_code == 404:
            print("   ❌ Endpoint no encontrado")
        else:
            print(f"   ⚠️  Respuesta: {response.text[:100]}...")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    print("🧪 PRUEBA DE ENDPOINTS PARA FLUTTER")
    print("=" * 50)
    
    # Endpoints que Flutter está buscando
    endpoints = [
        ("/finanzas/estado-cuenta-unificado/", "Estado Cuenta Unificado"),
        ("/finanzas/historial-pagos-unificados/", "Historial Pagos Unificados"),
        ("/finanzas/estado-de-cuenta/", "Estado de Cuenta Original"),
        ("/finanzas/pagos/", "Lista de Pagos"),
        ("/finanzas/gastos/", "Lista de Gastos"),
        ("/finanzas/multas/", "Lista de Multas"),
    ]
    
    for endpoint, nombre in endpoints:
        url = BASE_URL + endpoint
        test_endpoint(url, nombre)
    
    print("\n" + "=" * 50)
    print("📋 RESUMEN:")
    print("   - Si ve status 401: El endpoint existe pero requiere autenticación")
    print("   - Si ve status 404: El endpoint no existe")
    print("   - Si ve status 200: El endpoint funciona perfectamente")
    print("\n🔧 SOLUCIÓN PARA FLUTTER:")
    print("   - Asegúrate de enviar token de autenticación en headers")
    print("   - Usa: Authorization: Token <tu_token>")

if __name__ == "__main__":
    main()
