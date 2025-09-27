import requests
from django.conf import settings
from .models import Pago

def iniciar_pago_qr(pago_id):
    """
    Se comunica con PagosNet para generar una transacción QR.
    """
    try:
        pago = Pago.objects.get(id=pago_id)
    except Pago.DoesNotExist:
        return {"error": "El pago no existe."}

    # 1. Autenticación con la pasarela
    auth_url = f"{settings.PAGOSNET_API_URL}authentication/login"
    auth_payload = {
        "email": settings.PAGOSNET_EMAIL,
        "password": settings.PAGOSNET_PASSWORD
    }
    auth_response = requests.post(auth_url, json=auth_payload)
    if auth_response.status_code != 200:
        return {"error": "Fallo de autenticación con la pasarela."}
    
    token = auth_response.json().get('token')
    headers = {'Authorization': f'Bearer {token}'}

    # 2. Creación de la transacción
    transaction_url = f"{settings.PAGOSNET_API_URL}transaction/qrpago"
    transaction_payload = {
        "monto": float(pago.monto),
        "moneda": "BOB", # Bolivianos
        "glosa": f"Pago de cuota {pago.gasto.nombre}",
        "nombreCompleto": pago.usuario.get_full_name(),
        "carnetIdentidad": "0000000", # O un dato real si lo tienes
        "celular": "77777777", # O un dato real si lo tienes
        "email": pago.usuario.email,
        "empresa": "SmartCondominium",
        "tipoServicio": "Servicios Varios",
        "idExterno": str(pago.id) # Muy importante para identificar el pago después
    }

    qr_response = requests.post(transaction_url, json=transaction_payload, headers=headers)
    
    if qr_response.status_code == 200:
        qr_data = qr_response.json().get('data')
        # Guardamos la info del QR en nuestro modelo
        pago.qr_data = qr_data.get('qr')
        pago.id_transaccion_pasarela = qr_data.get('idTrn')
        pago.save()
        return {"qr_image_base64": pago.qr_data}
    
    return {"error": "No se pudo generar el QR.", "details": qr_response.json()}