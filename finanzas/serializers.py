import requests
from django.conf import settings
from .models import Pago
from rest_framework import serializers
from .models import Gasto, Pago, Multa
# En finanzas/serializers.py
from .models import Gasto, Pago, Multa, Reserva, Egreso, Ingreso # Importar nuevos modelos

from condominio.models import Reserva # <-- AÑADE ESTA LÍNEA
def iniciar_pago_qr(pago_id):
    """
    Se comunica con PagosNet para generar una transacción QR.
    """
    try:
        pago = Pago.objects.select_related('gasto', 'usuario').get(id=pago_id)
    except Pago.DoesNotExist:
        return {"error": "El pago no existe."}

    # 1. Autenticación (asume que tienes las credenciales en settings.py)
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
        # --- CORRECCIONES AQUÍ ---
        "monto": float(pago.monto_pagado), # Usamos monto_pagado
        "glosa": f"Pago: {pago.gasto.descripcion or 'Gasto General'}", # Usamos descripcion
        "nombreCompleto": pago.usuario.get_full_name() or pago.usuario.username,
        "carnetIdentidad": "0000000",
        "celular": "77777777",
        "email": pago.usuario.email,
        "empresa": "SmartCondominium",
        "tipoServicio": "Servicios Varios",
        "idExterno": str(pago.id)
    }

    qr_response = requests.post(transaction_url, json=transaction_payload, headers=headers)
    
    if qr_response.status_code == 200:
        qr_data = qr_response.json().get('data')
        pago.qr_data = qr_data.get('qr')
        pago.id_transaccion_pasarela = qr_data.get('idTrn')
        pago.save()
        return {"qr_image_base64": pago.qr_data}
    
    return {"error": "No se pudo generar el QR.", "details": qr_response.json()}

from django.utils import timezone
from datetime import timedelta

class GastoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gasto
        fields = '__all__'


class PagoMultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = '__all__'
# en finanzas/serializers.py

# ... (otras importaciones) ...

class PagoSerializer(serializers.ModelSerializer):
    # Añade este campo para que el usuario se muestre pero no se requiera al crear
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Pago
        # Especificamos los campos para asegurar que 'usuario' use nuestra definición
        fields = [
            'id', 'gasto', 'multa', 'reserva', 'usuario', 
            'monto_pagado', 'fecha_pago', 'comprobante', 
            'estado_pago', 'id_transaccion_pasarela', 'qr_data'
        ]

class MultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Multa
        fields = '__all__'
    

# Al final de finanzas/serializers.py
class ReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = '__all__'


class EgresoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Egreso
        fields = [
            'id', 'fecha', 'monto', 'concepto', 'descripcion',
            'categoria', 'comprobante', 'solicitud_mantenimiento'
        ]

class IngresoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingreso
        fields = [
            'id', 'fecha', 'monto', 'concepto', 'descripcion', 'pago_relacionado'
        ]