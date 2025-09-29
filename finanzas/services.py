# en finanzas/services.py

import requests
from django.conf import settings
from .models import Pago, Gasto 
from condominio.models import Propiedad
from django.utils import timezone
from datetime import timedelta
import uuid

# ¡Esta es la importación correcta!
from auditoria.services import registrar_evento

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

def es_residente_moroso(usuario, meses_limite=None):
    """
    Verifica si un usuario asociado a una propiedad tiene deudas vencidas.
    Si 'meses_limite' es un número, verifica deudas vencidas por más de esa cantidad de meses.
    """
    propiedades = Propiedad.objects.filter(propietario=usuario)
    if not propiedades.exists():
        return False # No es propietario, no tiene deudas de expensas

    hoy = timezone.now().date()

    # Construimos el query para gastos no pagados y vencidos
    query = Gasto.objects.filter(
        propiedad__in=propiedades,
        pagado=False,
        fecha_vencimiento__lt=hoy
    )

    if meses_limite:
        fecha_limite = hoy - timedelta(days=30 * meses_limite)
        query = query.filter(fecha_vencimiento__lt=fecha_limite)

    return query.exists()

def simular_pago_qr(pago_id):
    """
    Simula la generación y confirmación de un pago QR.
    """
    try:
        pago = Pago.objects.select_related('usuario').get(id=pago_id)
    except Pago.DoesNotExist:
        return {"error": "El pago no existe."}

    # Simula una transacción exitosa
    pago.id_transaccion_pasarela = f"sim_{uuid.uuid4()}" # Genera un ID de transacción falso
    pago.estado_pago = 'PAGADO'
    pago.fecha_pago = timezone.now()
    pago.save()

    # --- Auditoría ---
    registrar_evento(
        usuario=pago.usuario,
        ip="127.0.0.1", # IP del servidor, ya que es un proceso interno
        accion="Confirmación de Pago (Simulado)",
        extra_data={
            "pago_id": pago.id,
            "id_transaccion_simulada": pago.id_transaccion_pasarela,
            "monto": str(pago.monto_pagado),
            "realizado_por": "Sistema (Simulación)",
        }
    )
    # --- Fin Auditoría ---
    
    return {"mensaje": "Pago simulado y confirmado exitosamente."}