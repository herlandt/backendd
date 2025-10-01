import requests
from django.conf import settings
from django.db import models
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

    def validate_monto_pagado(self, value):
        """
        Valida que el monto del pago sea positivo y no exceda el saldo pendiente
        """
        if value <= 0:
            raise serializers.ValidationError("El monto del pago debe ser mayor a cero.")
        
        # Si estamos actualizando un pago existente, no validamos contra el saldo
        if self.instance:
            return value
        
        # Validar contra el saldo pendiente para nuevos pagos
        gasto = self.initial_data.get('gasto')
        multa = self.initial_data.get('multa')
        reserva = self.initial_data.get('reserva')
        
        saldo_pendiente = 0
        
        if gasto:
            try:
                gasto_obj = Gasto.objects.get(id=gasto)
                pagos_previos = Pago.objects.filter(gasto=gasto_obj).aggregate(
                    total=models.Sum('monto_pagado')
                )['total'] or 0
                saldo_pendiente = gasto_obj.monto - pagos_previos
            except Gasto.DoesNotExist:
                raise serializers.ValidationError("El gasto especificado no existe.")
                
        elif multa:
            try:
                multa_obj = Multa.objects.get(id=multa)
                pagos_previos = Pago.objects.filter(multa=multa_obj).aggregate(
                    total=models.Sum('monto_pagado')
                )['total'] or 0
                saldo_pendiente = multa_obj.monto - pagos_previos
            except Multa.DoesNotExist:
                raise serializers.ValidationError("La multa especificada no existe.")
                
        elif reserva:
            try:
                reserva_obj = Reserva.objects.get(id=reserva)
                pagos_previos = Pago.objects.filter(reserva=reserva_obj).aggregate(
                    total=models.Sum('monto_pagado')
                )['total'] or 0
                saldo_pendiente = reserva_obj.costo_total - pagos_previos
            except Reserva.DoesNotExist:
                raise serializers.ValidationError("La reserva especificada no existe.")
        
        if value > saldo_pendiente:
            raise serializers.ValidationError(
                f"El monto del pago (${value}) no puede exceder el saldo pendiente (${saldo_pendiente})."
            )
        
        return value

    def validate(self, data):
        """
        Validación a nivel de objeto: debe tener exactamente uno de gasto, multa o reserva
        """
        campos_pago = [data.get('gasto'), data.get('multa'), data.get('reserva')]
        campos_no_nulos = [campo for campo in campos_pago if campo is not None]
        
        if len(campos_no_nulos) != 1:
            raise serializers.ValidationError(
                "Debe especificar exactamente uno de: gasto, multa o reserva."
            )
        
        return data

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

# Serializadores específicos para las vistas que causan problemas de documentación
class GenerarExpensasRequestSerializer(serializers.Serializer):
    """Serializer para la solicitud de generar expensas masivas"""
    monto = serializers.DecimalField(max_digits=10, decimal_places=2, help_text="Monto de la expensa")
    descripcion = serializers.CharField(max_length=255, help_text="Descripción de la expensa")
    fecha_vencimiento = serializers.DateField(help_text="Fecha de vencimiento del pago")

class GenerarExpensasResponseSerializer(serializers.Serializer):
    """Serializer para la respuesta de generar expensas masivas"""
    mensaje = serializers.CharField(help_text="Mensaje de confirmación")

class EstadoDeCuentaResponseSerializer(serializers.Serializer):
    """Serializer para la respuesta del estado de cuenta"""
    id = serializers.IntegerField()
    propiedad = serializers.IntegerField(required=False)
    monto = serializers.DecimalField(max_digits=10, decimal_places=2)
    descripcion = serializers.CharField()
    fecha_emision = serializers.DateField(required=False)
    fecha_vencimiento = serializers.DateField(required=False)
    tipo_deuda = serializers.CharField(help_text="Tipo de deuda: gasto, multa o reserva")

# =============================================================================
# SERIALIZERS PARA DOCUMENTACIÓN DE VISTAS PROBLEMÁTICAS
# =============================================================================

class SimpleResponseSerializer(serializers.Serializer):
    """Serializer genérico para respuestas simples"""
    mensaje = serializers.CharField(help_text="Mensaje de respuesta")
    success = serializers.BooleanField(default=True, help_text="Estado de la operación")

class PDFResponseSerializer(serializers.Serializer):
    """Serializer para respuestas de archivos PDF"""
    file = serializers.FileField(help_text="Archivo PDF generado", read_only=True)

class SimularPagoRequestSerializer(serializers.Serializer):
    """Serializer para solicitudes de simulación de pago"""
    pago_id = serializers.IntegerField(help_text="ID del pago a simular")
    
class SimularPagoResponseSerializer(serializers.Serializer):
    """Serializer para respuestas de simulación de pago"""
    qr_data = serializers.CharField(help_text="Datos del código QR")
    monto = serializers.DecimalField(max_digits=10, decimal_places=2, help_text="Monto del pago")

class ReporteMorosidadResponseSerializer(serializers.Serializer):
    """Serializer para reporte de morosidad"""
    propiedades_morosas = serializers.IntegerField(help_text="Número de propiedades morosas")
    monto_total_deuda = serializers.DecimalField(max_digits=10, decimal_places=2, help_text="Monto total adeudado")

class WebhookStripeSerializer(serializers.Serializer):
    """Serializer para webhooks de Stripe"""
    id = serializers.CharField(help_text="ID del evento")
    type = serializers.CharField(help_text="Tipo de evento")
    data = serializers.DictField(help_text="Datos del evento")

class PagarReservaRequestSerializer(serializers.Serializer):
    """Serializer para pagar una reserva"""
    reserva_id = serializers.IntegerField(help_text="ID de la reserva a pagar")
    metodo_pago = serializers.CharField(help_text="Método de pago")

class ReporteUsoAreasComunesResponseSerializer(serializers.Serializer):
    """Serializer para reporte de uso de áreas comunes"""
    area = serializers.CharField(help_text="Nombre del área")
    total_reservas = serializers.IntegerField(help_text="Total de reservas")
    ingresos_generados = serializers.DecimalField(max_digits=10, decimal_places=2, help_text="Ingresos generados")