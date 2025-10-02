# 💳 GUÍA COMPLETA: INTEGRACIÓN DE STRIPE PARA MÓVIL

## 📋 **RESUMEN DE IMPLEMENTACIÓN**

Esta guía te ayudará a implementar un sistema completo de pagos con Stripe para tu aplicación móvil de condominio, incluyendo:
- Backend Django configurado con Stripe
- Flutter móvil con Stripe SDK
- Webhooks para confirmación de pagos
- Sistema de suscripciones para expensas mensuales

---

## 🏗️ **PARTE 1: CONFIGURACIÓN DEL BACKEND DJANGO**

### 1.1 **Instalar Dependencias**

```bash
# En tu backend Django
pip install stripe python-decouple
```

### 1.2 **Configurar Variables de Entorno**

```bash
# En tu archivo .env
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 1.3 **Actualizar Settings.py**

```python
# config/settings.py
from decouple import config

# Stripe Configuration
STRIPE_PUBLIC_KEY = config('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET')

# Add to INSTALLED_APPS if not present
INSTALLED_APPS = [
    # ... otras apps
    'corsheaders',  # Para permitir requests desde móvil
]

# CORS settings para móvil
CORS_ALLOW_ALL_ORIGINS = True  # Solo para desarrollo
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Agrega las URLs de tu app móvil
]
```

### 1.4 **Crear Servicio de Stripe**

```python
# finanzas/stripe_service.py
import stripe
from django.conf import settings
from decimal import Decimal
import logging

stripe.api_key = settings.STRIPE_SECRET_KEY
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
    def create_subscription(customer_id, price_id, metadata=None):
        """
        Crea una suscripción para pagos recurrentes (expensas)
        """
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': price_id}],
                metadata=metadata or {},
                expand=['latest_invoice.payment_intent']
            )
            return {
                'success': True,
                'subscription_id': subscription.id,
                'client_secret': subscription.latest_invoice.payment_intent.client_secret,
                'subscription': subscription
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe Subscription error: {e}")
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
```

### 1.5 **Actualizar Modelos para Stripe**

```python
# finanzas/models.py - Agregar campos para Stripe

class Pago(models.Model):
    # ... campos existentes ...
    
    # Campos para Stripe
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_payment_method_id = models.CharField(max_length=255, blank=True, null=True)
    
    class EstadoPago(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        PROCESANDO = "PROCESANDO", "Procesando"
        COMPLETADO = "COMPLETADO", "Completado"
        FALLIDO = "FALLIDO", "Fallido"
        CANCELADO = "CANCELADO", "Cancelado"
        REEMBOLSADO = "REEMBOLSADO", "Reembolsado"
    
    estado_pago = models.CharField(
        max_length=20, 
        choices=EstadoPago.choices, 
        default=EstadoPago.PENDIENTE
    )

# Nuevo modelo para clientes Stripe
class StripeCustomer(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Stripe Customer: {self.user.username}"

# Modelo para suscripciones (expensas mensuales)
class SuscripcionExpensa(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    stripe_price_id = models.CharField(max_length=255)
    monto_mensual = models.DecimalField(max_digits=10, decimal_places=2)
    activa = models.BooleanField(default=True)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Suscripción {self.user.username} - ${self.monto_mensual}"
```

---

## 🏗️ **PARTE 2: VISTAS Y ENDPOINTS PARA STRIPE**

### 2.1 **Crear Payment Intent (Pago único)**

```python
# finanzas/views.py - Agregar estas vistas

from .stripe_service import StripePaymentService
from .models import StripeCustomer, SuscripcionExpensa

class CreatePaymentIntentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Crea un Payment Intent para un pago único
        Body: {
            "gasto_id": 123,
            "monto": 150.00,
            "descripcion": "Pago de expensa Enero 2025"
        }
        """
        try:
            gasto_id = request.data.get('gasto_id')
            monto = Decimal(str(request.data.get('monto', 0)))
            descripcion = request.data.get('descripcion', '')
            
            # Validar gasto
            try:
                gasto = Gasto.objects.get(id=gasto_id, usuario=request.user)
            except Gasto.DoesNotExist:
                return Response({
                    'error': 'Gasto no encontrado'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Convertir a centavos
            amount_cents = int(monto * 100)
            
            # Obtener o crear cliente Stripe
            stripe_customer, created = StripeCustomer.objects.get_or_create(
                user=request.user,
                defaults={
                    'stripe_customer_id': ''
                }
            )
            
            if created or not stripe_customer.stripe_customer_id:
                # Crear cliente en Stripe
                customer_result = StripePaymentService.create_customer(
                    email=request.user.email,
                    name=f"{request.user.first_name} {request.user.last_name}",
                    metadata={
                        'user_id': request.user.id,
                        'username': request.user.username
                    }
                )
                
                if customer_result['success']:
                    stripe_customer.stripe_customer_id = customer_result['customer_id']
                    stripe_customer.save()
                else:
                    return Response({
                        'error': 'Error creando cliente en Stripe'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Crear Payment Intent
            payment_result = StripePaymentService.create_payment_intent(
                amount_cents=amount_cents,
                currency='usd',
                metadata={
                    'user_id': request.user.id,
                    'gasto_id': gasto_id,
                    'descripcion': descripcion
                }
            )
            
            if payment_result['success']:
                # Crear registro de pago pendiente
                pago = Pago.objects.create(
                    gasto=gasto,
                    usuario=request.user,
                    monto_pagado=monto,
                    estado_pago=Pago.EstadoPago.PENDIENTE,
                    stripe_payment_intent_id=payment_result['payment_intent_id'],
                    stripe_customer_id=stripe_customer.stripe_customer_id
                )
                
                return Response({
                    'success': True,
                    'client_secret': payment_result['client_secret'],
                    'payment_intent_id': payment_result['payment_intent_id'],
                    'pago_id': pago.id,
                    'amount': payment_result['amount'],
                    'currency': payment_result['currency']
                })
            else:
                return Response({
                    'error': payment_result['error']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
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
        """
        try:
            # Obtener o crear cliente Stripe
            stripe_customer, created = StripeCustomer.objects.get_or_create(
                user=request.user,
                defaults={'stripe_customer_id': ''}
            )
            
            if created or not stripe_customer.stripe_customer_id:
                # Crear cliente en Stripe
                customer_result = StripePaymentService.create_customer(
                    email=request.user.email,
                    name=f"{request.user.first_name} {request.user.last_name}",
                    metadata={'user_id': request.user.id}
                )
                
                if customer_result['success']:
                    stripe_customer.stripe_customer_id = customer_result['customer_id']
                    stripe_customer.save()
                else:
                    return Response({
                        'error': 'Error creando cliente en Stripe'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Crear Setup Intent
            setup_result = StripePaymentService.create_setup_intent(
                customer_id=stripe_customer.stripe_customer_id,
                metadata={'user_id': request.user.id}
            )
            
            if setup_result['success']:
                return Response({
                    'success': True,
                    'client_secret': setup_result['client_secret'],
                    'setup_intent_id': setup_result['setup_intent_id']
                })
            else:
                return Response({
                    'error': setup_result['error']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error creating setup intent: {e}")
            return Response({
                'error': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StripeWebhookView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Webhook de Stripe para confirmar pagos
        """
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return Response({'error': 'Invalid payload'}, status=400)
        except stripe.error.SignatureVerificationError:
            return Response({'error': 'Invalid signature'}, status=400)
        
        # Manejar eventos
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            self._handle_payment_success(payment_intent)
            
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            self._handle_payment_failure(payment_intent)
            
        elif event['type'] == 'invoice.payment_succeeded':
            invoice = event['data']['object']
            self._handle_subscription_payment(invoice)
        
        return Response({'status': 'success'})
    
    def _handle_payment_success(self, payment_intent):
        """Maneja el éxito de un pago"""
        try:
            pago = Pago.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            pago.estado_pago = Pago.EstadoPago.COMPLETADO
            pago.fecha_pago = timezone.now()
            pago.save()
            
            # Registrar evento de auditoría
            registrar_evento(
                usuario=pago.usuario,
                accion="Pago Completado via Stripe",
                detalles=f"Pago ID: {pago.id}, Monto: ${pago.monto_pagado}",
                ip_address="stripe_webhook"
            )
            
        except Pago.DoesNotExist:
            logger.error(f"Pago no encontrado para payment_intent: {payment_intent['id']}")
    
    def _handle_payment_failure(self, payment_intent):
        """Maneja el fallo de un pago"""
        try:
            pago = Pago.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            pago.estado_pago = Pago.EstadoPago.FALLIDO
            pago.save()
            
        except Pago.DoesNotExist:
            logger.error(f"Pago no encontrado para payment_intent fallido: {payment_intent['id']}")
    
    def _handle_subscription_payment(self, invoice):
        """Maneja pagos de suscripción (expensas mensuales)"""
        try:
            subscription_id = invoice['subscription']
            suscripcion = SuscripcionExpensa.objects.get(
                stripe_subscription_id=subscription_id
            )
            
            # Crear gasto automático por la expensa mensual
            gasto = Gasto.objects.create(
                usuario=suscripcion.user,
                monto=suscripcion.monto_mensual,
                descripcion=f"Expensa mensual - {timezone.now().strftime('%B %Y')}",
                fecha_emision=timezone.now().date(),
                fecha_vencimiento=timezone.now().date() + timedelta(days=30)
            )
            
            # Crear pago automático
            Pago.objects.create(
                gasto=gasto,
                usuario=suscripcion.user,
                monto_pagado=suscripcion.monto_mensual,
                estado_pago=Pago.EstadoPago.COMPLETADO,
                fecha_pago=timezone.now(),
                stripe_customer_id=invoice['customer']
            )
            
        except SuscripcionExpensa.DoesNotExist:
            logger.error(f"Suscripción no encontrada: {subscription_id}")
```

### 2.2 **Actualizar URLs**

```python
# finanzas/urls.py - Agregar nuevas rutas

from .views import (
    CreatePaymentIntentView, CreateSetupIntentView, StripeWebhookView
)

urlpatterns = [
    # ... rutas existentes ...
    
    # Stripe endpoints
    path("stripe/create-payment-intent/", CreatePaymentIntentView.as_view(), name="stripe-payment-intent"),
    path("stripe/create-setup-intent/", CreateSetupIntentView.as_view(), name="stripe-setup-intent"),
    path("stripe/webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
]
```

---

## 📱 **PARTE 3: IMPLEMENTACIÓN EN FLUTTER/DART**

### 3.1 **Dependencias para Flutter**

```yaml
# pubspec.yaml
dependencies:
  flutter:
    sdk: flutter
  
  # Stripe
  flutter_stripe: ^10.1.1
  
  # HTTP y estado
  http: ^1.1.0
  provider: ^6.1.1
  
  # Almacenamiento local
  shared_preferences: ^2.2.2
  
  # Manejo de JSON
  json_annotation: ^4.8.1

dev_dependencies:
  flutter_test:
    sdk: flutter
  json_serializable: ^6.7.1
  build_runner: ^2.4.7
```

### 3.2 **Configuración de Stripe en Flutter**

```dart
// lib/main.dart
import 'package:flutter/material.dart';
import 'package:flutter_stripe/flutter_stripe.dart';
import 'package:provider/provider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Configurar Stripe
  Stripe.publishableKey = 'pk_test_...'; // Tu clave pública de Stripe
  await Stripe.instance.applySettings();
  
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => PaymentProvider()),
        ChangeNotifierProvider(create: (_) => AuthProvider()),
      ],
      child: MaterialApp(
        title: 'Smart Condominio',
        theme: ThemeData(
          primarySwatch: Colors.blue,
        ),
        home: LoginScreen(),
      ),
    );
  }
}
```

### 3.3 **Servicio de API**

```dart
// lib/services/api_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String baseUrl = 'http://your-backend-url.com/api';
  
  static Future<String?> _getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('auth_token');
  }
  
  static Future<Map<String, String>> _getHeaders() async {
    final token = await _getToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Token $token',
    };
  }
  
  // Crear Payment Intent
  static Future<Map<String, dynamic>> createPaymentIntent({
    required int gastoId,
    required double monto,
    required String descripcion,
  }) async {
    try {
      final headers = await _getHeaders();
      final response = await http.post(
        Uri.parse('$baseUrl/finanzas/stripe/create-payment-intent/'),
        headers: headers,
        body: jsonEncode({
          'gasto_id': gastoId,
          'monto': monto,
          'descripcion': descripcion,
        }),
      );
      
      if (response.statusCode == 200) {
        return {
          'success': true,
          'data': jsonDecode(response.body),
        };
      } else {
        return {
          'success': false,
          'error': 'Error: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }
  
  // Crear Setup Intent (para guardar tarjeta)
  static Future<Map<String, dynamic>> createSetupIntent() async {
    try {
      final headers = await _getHeaders();
      final response = await http.post(
        Uri.parse('$baseUrl/finanzas/stripe/create-setup-intent/'),
        headers: headers,
      );
      
      if (response.statusCode == 200) {
        return {
          'success': true,
          'data': jsonDecode(response.body),
        };
      } else {
        return {
          'success': false,
          'error': 'Error: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }
  
  // Obtener gastos pendientes
  static Future<Map<String, dynamic>> getGastosPendientes() async {
    try {
      final headers = await _getHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/finanzas/estado-de-cuenta/'),
        headers: headers,
      );
      
      if (response.statusCode == 200) {
        return {
          'success': true,
          'data': jsonDecode(response.body),
        };
      } else {
        return {
          'success': false,
          'error': 'Error: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }
}
```

### 3.4 **Provider para Manejo de Estado**

```dart
// lib/providers/payment_provider.dart
import 'package:flutter/material.dart';
import 'package:flutter_stripe/flutter_stripe.dart';
import '../services/api_service.dart';

class PaymentProvider with ChangeNotifier {
  bool _isLoading = false;
  String? _error;
  List<dynamic> _gastosPendientes = [];
  
  bool get isLoading => _isLoading;
  String? get error => _error;
  List<dynamic> get gastosPendientes => _gastosPendientes;
  
  // Cargar gastos pendientes
  Future<void> loadGastosPendientes() async {
    _setLoading(true);
    _error = null;
    
    final result = await ApiService.getGastosPendientes();
    
    if (result['success']) {
      _gastosPendientes = result['data'];
    } else {
      _error = result['error'];
    }
    
    _setLoading(false);
  }
  
  // Procesar pago con Stripe
  Future<bool> processPayment({
    required int gastoId,
    required double monto,
    required String descripcion,
  }) async {
    _setLoading(true);
    _error = null;
    
    try {
      // 1. Crear Payment Intent en el backend
      final paymentIntentResult = await ApiService.createPaymentIntent(
        gastoId: gastoId,
        monto: monto,
        descripcion: descripcion,
      );
      
      if (!paymentIntentResult['success']) {
        _error = paymentIntentResult['error'];
        _setLoading(false);
        return false;
      }
      
      final clientSecret = paymentIntentResult['data']['client_secret'];
      
      // 2. Confirmar pago con Stripe
      await Stripe.instance.confirmPayment(
        paymentIntentClientSecret: clientSecret,
        data: PaymentMethodData(
          billingDetails: BillingDetails(
            name: 'Usuario',
            email: 'usuario@example.com',
          ),
        ),
      );
      
      // 3. Recargar gastos
      await loadGastosPendientes();
      
      _setLoading(false);
      return true;
      
    } catch (e) {
      _error = 'Error procesando pago: ${e.toString()}';
      _setLoading(false);
      return false;
    }
  }
  
  // Guardar método de pago
  Future<bool> savePaymentMethod() async {
    _setLoading(true);
    _error = null;
    
    try {
      // 1. Crear Setup Intent
      final setupIntentResult = await ApiService.createSetupIntent();
      
      if (!setupIntentResult['success']) {
        _error = setupIntentResult['error'];
        _setLoading(false);
        return false;
      }
      
      final clientSecret = setupIntentResult['data']['client_secret'];
      
      // 2. Confirmar Setup Intent
      await Stripe.instance.confirmSetupIntent(
        paymentIntentClientSecret: clientSecret,
        data: PaymentMethodData(
          billingDetails: BillingDetails(
            name: 'Usuario',
            email: 'usuario@example.com',
          ),
        ),
      );
      
      _setLoading(false);
      return true;
      
    } catch (e) {
      _error = 'Error guardando método de pago: ${e.toString()}';
      _setLoading(false);
      return false;
    }
  }
  
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }
  
  void clearError() {
    _error = null;
    notifyListeners();
  }
}
```

### 3.5 **UI para Pagos**

```dart
// lib/screens/payments_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/payment_provider.dart';

class PaymentsScreen extends StatefulWidget {
  @override
  _PaymentsScreenState createState() => _PaymentsScreenState();
}

class _PaymentsScreenState extends State<PaymentsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<PaymentProvider>().loadGastosPendientes();
    });
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('💳 Pagos'),
        backgroundColor: Colors.blue[700],
      ),
      body: Consumer<PaymentProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('Cargando...'),
                ],
              ),
            );
          }
          
          if (provider.error != null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.error, size: 64, color: Colors.red),
                  SizedBox(height: 16),
                  Text(
                    'Error: ${provider.error}',
                    style: TextStyle(color: Colors.red),
                    textAlign: TextAlign.center,
                  ),
                  SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () {
                      provider.clearError();
                      provider.loadGastosPendientes();
                    },
                    child: Text('Reintentar'),
                  ),
                ],
              ),
            );
          }
          
          if (provider.gastosPendientes.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.check_circle, size: 64, color: Colors.green),
                  SizedBox(height: 16),
                  Text(
                    '¡No tienes gastos pendientes!',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            );
          }
          
          return ListView.builder(
            padding: EdgeInsets.all(16),
            itemCount: provider.gastosPendientes.length,
            itemBuilder: (context, index) {
              final gasto = provider.gastosPendientes[index];
              return _buildGastoCard(context, gasto, provider);
            },
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showSavePaymentMethodDialog(context),
        child: Icon(Icons.credit_card),
        tooltip: 'Guardar método de pago',
      ),
    );
  }
  
  Widget _buildGastoCard(BuildContext context, dynamic gasto, PaymentProvider provider) {
    return Card(
      margin: EdgeInsets.only(bottom: 16),
      elevation: 4,
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  gasto['descripcion'] ?? 'Sin descripción',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  '\$${gasto['monto']}',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.green[700],
                  ),
                ),
              ],
            ),
            SizedBox(height: 8),
            if (gasto['fecha_vencimiento'] != null)
              Text(
                'Vencimiento: ${gasto['fecha_vencimiento']}',
                style: TextStyle(color: Colors.grey[600]),
              ),
            SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () => _processPayment(context, gasto, provider),
                icon: Icon(Icons.payment),
                label: Text('Pagar con Stripe'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue[700],
                  foregroundColor: Colors.white,
                  padding: EdgeInsets.symmetric(vertical: 12),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Future<void> _processPayment(BuildContext context, dynamic gasto, PaymentProvider provider) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('Confirmar Pago'),
          content: Text(
            '¿Deseas pagar \$${gasto['monto']} por "${gasto['descripcion']}"?',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: Text('Cancelar'),
            ),
            ElevatedButton(
              onPressed: () => Navigator.of(context).pop(true),
              child: Text('Pagar'),
            ),
          ],
        );
      },
    );
    
    if (confirmed == true) {
      final success = await provider.processPayment(
        gastoId: gasto['id'],
        monto: double.parse(gasto['monto'].toString()),
        descripcion: gasto['descripcion'] ?? '',
      );
      
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('✅ Pago procesado exitosamente'),
            backgroundColor: Colors.green,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Error procesando pago'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
  
  Future<void> _showSavePaymentMethodDialog(BuildContext context) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('Guardar Método de Pago'),
          content: Text(
            'Esto te permitirá guardar tu tarjeta para pagos futuros más rápidos.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: Text('Cancelar'),
            ),
            ElevatedButton(
              onPressed: () => Navigator.of(context).pop(true),
              child: Text('Continuar'),
            ),
          ],
        );
      },
    );
    
    if (confirmed == true) {
      final provider = context.read<PaymentProvider>();
      final success = await provider.savePaymentMethod();
      
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('✅ Método de pago guardado'),
            backgroundColor: Colors.green,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Error guardando método de pago'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
}
```

---

## 🔄 **PARTE 4: MIGRACIÓN Y TESTING**

### 4.1 **Crear Migraciones**

```bash
cd c:\Users\asus\Documents\desplegable\backendd
python manage.py makemigrations finanzas
python manage.py migrate
```

### 4.2 **Script de Testing**

```python
# test_stripe_integration.py
#!/usr/bin/env python3
"""
🧪 PRUEBA DE INTEGRACIÓN STRIPE
"""

import os
import sys
import django
import stripe

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from finanzas.stripe_service import StripePaymentService
from django.contrib.auth.models import User
from finanzas.models import Gasto

def test_stripe_service():
    print("🧪 PROBANDO SERVICIO DE STRIPE")
    print("=" * 50)
    
    # 1. Crear cliente
    customer_result = StripePaymentService.create_customer(
        email="test@example.com",
        name="Usuario Test",
        metadata={"test": "true"}
    )
    
    print("1. 👤 Crear Cliente:")
    print(f"   ✅ Éxito: {customer_result['success']}")
    if customer_result['success']:
        print(f"   🆔 Customer ID: {customer_result['customer_id']}")
    else:
        print(f"   ❌ Error: {customer_result['error']}")
    
    # 2. Crear Payment Intent
    payment_result = StripePaymentService.create_payment_intent(
        amount_cents=1500,  # $15.00
        currency='usd',
        metadata={"test_payment": "true"}
    )
    
    print("\n2. 💳 Crear Payment Intent:")
    print(f"   ✅ Éxito: {payment_result['success']}")
    if payment_result['success']:
        print(f"   🔑 Client Secret: {payment_result['client_secret'][:20]}...")
        print(f"   💰 Amount: ${payment_result['amount']/100}")
    else:
        print(f"   ❌ Error: {payment_result['error']}")

if __name__ == "__main__":
    test_stripe_service()
```

---

## 📚 **PARTE 5: DOCUMENTACIÓN Y CONFIGURACIÓN**

### 5.1 **Variables de Entorno Requeridas**

```bash
# .env - Variables necesarias para Stripe
STRIPE_PUBLIC_KEY=pk_test_51...  # Clave pública (para frontend)
STRIPE_SECRET_KEY=sk_test_51...  # Clave secreta (para backend)
STRIPE_WEBHOOK_SECRET=whsec_...  # Secret para webhooks
```

### 5.2 **Configuración de Webhooks en Stripe Dashboard**

1. **Ir a Stripe Dashboard → Webhooks**
2. **Crear endpoint:** `https://tu-backend.com/api/finanzas/stripe/webhook/`
3. **Eventos a escuchar:**
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `invoice.payment_succeeded`
   - `setup_intent.succeeded`

### 5.3 **Checklist de Implementación**

- [ ] ✅ **Backend configurado** con Stripe SDK
- [ ] ✅ **Modelos actualizados** con campos de Stripe
- [ ] ✅ **Vistas de API** para Payment Intent y Setup Intent
- [ ] ✅ **Webhook endpoint** configurado
- [ ] ✅ **Flutter configurado** con flutter_stripe
- [ ] ✅ **UI móvil** para procesar pagos
- [ ] ✅ **Testing** de integración completa
- [ ] ✅ **Variables de entorno** configuradas
- [ ] ✅ **Webhooks registrados** en Stripe Dashboard

---

## 🚀 **SIGUIENTES PASOS**

1. **Implementar el backend** con las vistas y servicios Stripe
2. **Actualizar los modelos** y ejecutar migraciones
3. **Configurar Flutter** con las dependencias Stripe
4. **Crear las pantallas** de pago en la app móvil
5. **Configurar webhooks** en Stripe Dashboard
6. **Probar el flujo completo** end-to-end

Con esta implementación tendrás un sistema completo de pagos móviles integrado con Stripe, incluyendo pagos únicos, métodos guardados y suscripciones para expensas mensuales. 🎉