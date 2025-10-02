# finanzas/stripe_service.py
import stripe
from django.conf import settings
from decimal import Decimal
import logging

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', 'sk_test_...')
logger = logging.getLogger(__name__)

class StripePaymentService:
    
    @staticmethod
    def create_payment_intent(amount_cents, currency='usd', metadata=None):
        """
        Crea un Payment Intent en Stripe
        amount_cents: Monto en centavos (ej: 1500 = $15.00)
        """
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount_cents),
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            return {
                'success': True,
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'amount': intent.amount,
                'currency': intent.currency
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def create_setup_intent(customer_id=None, metadata=None):
        """
        Crea un Setup Intent para guardar métodos de pago
        """
        try:
            setup_intent = stripe.SetupIntent.create(
                customer=customer_id,
                usage='off_session',
                metadata=metadata or {}
            )
            return {
                'success': True,
                'client_secret': setup_intent.client_secret,
                'setup_intent_id': setup_intent.id
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe Setup Intent error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def create_customer(email, name, metadata=None):
        """
        Crea un cliente en Stripe
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            return {
                'success': True,
                'customer_id': customer.id,
                'customer': customer
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe Customer error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def retrieve_payment_intent(payment_intent_id):
        """
        Obtiene información de un Payment Intent
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                'success': True,
                'payment_intent': intent,
                'status': intent.status,
                'amount': intent.amount,
                'currency': intent.currency
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe retrieve error: {e}")
            return {
                'success': False,
                'error': str(e)
            }