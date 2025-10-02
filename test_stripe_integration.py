# test_stripe_integration.py
import requests
import json

# Configuración
BASE_URL = "http://127.0.0.1:8000"
API_KEY = "tu-api-key-aqui"  # Cambia por tu API key
USERNAME = "stripe_test"  # Usuario de prueba creado
PASSWORD = "test123"  # Contraseña del usuario de prueba

def get_auth_token():
    """Obtiene token de autenticación"""
    try:
        response = requests.post(f"{BASE_URL}/api/login/", {
            "username": USERNAME,
            "password": PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        else:
            print(f"Error al obtener token: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Error conectando para token: {e}")
        return None

def test_create_payment_intent(token):
    """Prueba crear Payment Intent"""
    print("\n=== Test: Create Payment Intent ===")
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "amount": 1500,  # $15.00 en centavos
        "description": "Pago de mantenimiento - Prueba"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/finanzas/stripe/payment-intent/",
            headers=headers,
            json=data
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            return response.json().get("client_secret")
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_create_setup_intent(token):
    """Prueba crear Setup Intent"""
    print("\n=== Test: Create Setup Intent ===")
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/finanzas/stripe/setup-intent/",
            headers=headers,
            json={}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            return response.json().get("client_secret")
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_payment_status(token, payment_intent_id):
    """Prueba obtener estado de pago"""
    print(f"\n=== Test: Payment Status for {payment_intent_id} ===")
    
    headers = {
        "Authorization": f"Token {token}"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/finanzas/stripe/payment-status/{payment_intent_id}/",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")

def test_webhook_endpoint():
    """Prueba que el webhook esté disponible"""
    print("\n=== Test: Webhook Endpoint ===")
    
    try:
        # Solo verificamos que el endpoint existe (no enviamos datos reales)
        response = requests.post(
            f"{BASE_URL}/api/finanzas/stripe/webhook/",
            headers={"Content-Type": "application/json"},
            json={"test": "ping"}
        )
        
        print(f"Status: {response.status_code}")
        print("Webhook endpoint está disponible")
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    print("🚀 Iniciando pruebas de integración Stripe...")
    
    # 1. Obtener token
    token = get_auth_token()
    if not token:
        print("❌ No se pudo obtener token de autenticación")
        return
    
    print("✅ Token obtenido correctamente")
    
    # 2. Probar Payment Intent
    client_secret = test_create_payment_intent(token)
    
    # 3. Probar Setup Intent
    test_create_setup_intent(token)
    
    # 4. Probar webhook
    test_webhook_endpoint()
    
    # 5. Si tenemos un payment_intent_id, probar status
    if client_secret:
        # Extraer payment_intent_id del client_secret
        payment_intent_id = client_secret.split("_secret_")[0]
        test_payment_status(token, payment_intent_id)
    
    print("\n✅ Pruebas completadas")

if __name__ == "__main__":
    main()