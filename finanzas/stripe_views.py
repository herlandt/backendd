# finanzas/stripe_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.conf import settings
import stripe
import json
import logging

from .stripe_service import StripePaymentService
from .models import Pago
from .serializers import PagoSerializer

User = get_user_model()
logger = logging.getLogger(__name__)

class CreatePaymentIntentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Crea un Payment Intent para procesar pago
        POST /api/finanzas/stripe/payment-intent/
        {
            "amount": 1500,  // en centavos
            "description": "Pago de mantenimiento"
        }
        """
        try:
            amount = request.data.get('amount')
            description = request.data.get('description', '')
            
            if not amount or amount <= 0:
                return Response({
                    'error': 'Monto requerido y debe ser mayor a 0'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Metadata para rastrear el pago
            metadata = {
                'user_id': str(request.user.id),
                'user_email': request.user.email,
                'description': description
            }
            
            result = StripePaymentService.create_payment_intent(
                amount_cents=amount,
                metadata=metadata
            )
            
            if result['success']:
                return Response({
                    'client_secret': result['client_secret'],
                    'payment_intent_id': result['payment_intent_id'],
                    'amount': result['amount'],
                    'currency': result['currency']
                })
            else:
                return Response({
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error creating payment intent: {e}")
            return Response({
                'error': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreateSetupIntentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Crea un Setup Intent para guardar método de pago
        POST /api/finanzas/stripe/setup-intent/
        """
        try:
            # Crear o obtener customer de Stripe
            user = request.user
            stripe_customer_id = getattr(user, 'stripe_customer_id', None)
            
            if not stripe_customer_id:
                customer_result = StripePaymentService.create_customer(
                    email=user.email,
                    name=f"{user.first_name} {user.last_name}",
                    metadata={'user_id': str(user.id)}
                )
                
                if customer_result['success']:
                    stripe_customer_id = customer_result['customer_id']
                    # Aquí guardarías el customer_id en el modelo User
                    # user.stripe_customer_id = stripe_customer_id
                    # user.save()
                else:
                    return Response({
                        'error': customer_result['error']
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            result = StripePaymentService.create_setup_intent(
                customer_id=stripe_customer_id,
                metadata={'user_id': str(user.id)}
            )
            
            if result['success']:
                return Response({
                    'client_secret': result['client_secret'],
                    'setup_intent_id': result['setup_intent_id']
                })
            else:
                return Response({
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error creating setup intent: {e}")
            return Response({
                'error': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """
    Maneja los webhooks de Stripe
    POST /api/finanzas/stripe/webhook/
    """
    permission_classes = []  # Sin autenticación para webhooks
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            logger.error("Invalid payload")
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid signature")
            return HttpResponse(status=400)
        
        # Manejar diferentes tipos de eventos
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            self.handle_successful_payment(payment_intent)
            
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            self.handle_failed_payment(payment_intent)
            
        elif event['type'] == 'setup_intent.succeeded':
            setup_intent = event['data']['object']
            self.handle_setup_intent_succeeded(setup_intent)
        
        return HttpResponse(status=200)
    
    def handle_successful_payment(self, payment_intent):
        """
        Maneja pagos exitosos
        """
        try:
            metadata = payment_intent.get('metadata', {})
            user_id = metadata.get('user_id')
            description = metadata.get('description', '')
            
            if user_id:
                user = User.objects.get(id=user_id)
                
                # Crear registro de pago en la base de datos
                pago = Pago.objects.create(
                    usuario=user,
                    monto=payment_intent['amount'] / 100,  # Convertir de centavos
                    descripcion=description,
                    stripe_payment_intent_id=payment_intent['id'],
                    estado='COMPLETADO'
                )
                
                logger.info(f"Pago exitoso registrado: {pago.id}")
                
        except Exception as e:
            logger.error(f"Error handling successful payment: {e}")
    
    def handle_failed_payment(self, payment_intent):
        """
        Maneja pagos fallidos
        """
        try:
            metadata = payment_intent.get('metadata', {})
            user_id = metadata.get('user_id')
            
            logger.warning(f"Pago fallido para usuario {user_id}: {payment_intent['id']}")
            
        except Exception as e:
            logger.error(f"Error handling failed payment: {e}")
    
    def handle_setup_intent_succeeded(self, setup_intent):
        """
        Maneja setup intent exitoso (método de pago guardado)
        """
        try:
            metadata = setup_intent.get('metadata', {})
            user_id = metadata.get('user_id')
            
            logger.info(f"Setup Intent exitoso para usuario {user_id}: {setup_intent['id']}")
            
        except Exception as e:
            logger.error(f"Error handling setup intent: {e}")

class PaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, payment_intent_id):
        """
        Obtiene el estado de un Payment Intent
        GET /api/finanzas/stripe/payment-status/{payment_intent_id}/
        """
        try:
            result = StripePaymentService.retrieve_payment_intent(payment_intent_id)
            
            if result['success']:
                return Response({
                    'status': result['status'],
                    'amount': result['amount'],
                    'currency': result['currency']
                })
            else:
                return Response({
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error retrieving payment status: {e}")
            return Response({
                'error': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)