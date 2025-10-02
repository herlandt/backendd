# 🏢 GUÍA DEFINITIVA: Sistema de Pagos Móvil con Stripe

## 📋 Índice
1. [Configuración Backend Django](#backend)
2. [Configuración Stripe Dashboard](#stripe-config)
3. [Implementación Flutter](#flutter)
4. [Testing y Debugging](#testing)
5. [Producción y Deploy](#produccion)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Backend Django - ¡YA IMPLEMENTADO!

### ✅ Estado Actual del Backend
El backend ya está completamente configurado con:

- ✅ **Stripe Service**: `finanzas/stripe_service.py`
- ✅ **API Views**: `finanzas/stripe_views.py` 
- ✅ **URLs configuradas**: `/api/finanzas/stripe/`
- ✅ **Migraciones aplicadas**: Campos Stripe en modelo Pago
- ✅ **Dependencias instaladas**: `stripe==13.0.0`

### 🔧 Endpoints Disponibles

```bash
# 1. Crear Payment Intent (para procesar pago)
POST /api/finanzas/stripe/payment-intent/
Authorization: Bearer {token}
{
  "amount": 1500,  // $15.00 en centavos
  "description": "Pago de mantenimiento"
}

# 2. Crear Setup Intent (para guardar método de pago)
POST /api/finanzas/stripe/setup-intent/
Authorization: Bearer {token}

# 3. Webhook para confirmaciones
POST /api/finanzas/stripe/webhook/
# No requiere autenticación - manejado por Stripe

# 4. Verificar estado de pago
GET /api/finanzas/stripe/payment-status/{payment_intent_id}/
Authorization: Bearer {token}
```

---

## ⚙️ Configuración Stripe Dashboard

### 1. Crear Cuenta Stripe
```bash
# 1. Ve a https://stripe.com y crea una cuenta
# 2. Activa modo de desarrollo (Test Mode)
# 3. Obtén las claves API
```

### 2. Configurar Variables de Entorno
```bash
# Crea archivo .env en la raíz del proyecto
cp .env.example .env

# Edita .env con tus claves de Stripe:
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxxxxxxxxxx
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxxx
```

### 3. Configurar Webhook en Stripe Dashboard
```bash
# 1. Ve a Stripe Dashboard → Developers → Webhooks
# 2. Añade endpoint: https://tu-dominio.com/api/finanzas/stripe/webhook/
# 3. Selecciona eventos:
#    - payment_intent.succeeded
#    - payment_intent.payment_failed
#    - setup_intent.succeeded
# 4. Copia el Signing Secret al .env como STRIPE_WEBHOOK_SECRET
```

---

## 📱 Implementación Flutter

### 1. Dependencias en pubspec.yaml
```yaml
dependencies:
  flutter:
    sdk: flutter
  # Pagos con Stripe
  flutter_stripe: ^10.1.1
  # HTTP requests
  http: ^1.1.0
  # Estado global
  provider: ^6.1.1
  # Almacenamiento local
  shared_preferences: ^2.2.2
  # UI adicional
  fluttertoast: ^8.2.4
```

### 2. Configuración Inicial - main.dart
```dart
// lib/main.dart
import 'package:flutter/material.dart';
import 'package:flutter_stripe/flutter_stripe.dart';
import 'package:provider/provider.dart';
import 'services/stripe_service.dart';
import 'services/auth_service.dart';
import 'screens/payment_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Configurar Stripe
  Stripe.publishableKey = "pk_test_tu_clave_publica_aqui";
  await Stripe.instance.applySettings();
  
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthService()),
        ChangeNotifierProvider(create: (_) => StripeService()),
      ],
      child: MaterialApp(
        title: 'Condominio App',
        theme: ThemeData(
          primarySwatch: Colors.blue,
          visualDensity: VisualDensity.adaptivePlatformDensity,
        ),
        home: PaymentScreen(),
      ),
    );
  }
}
```

### 3. Servicio de Stripe - stripe_service.dart
```dart
// lib/services/stripe_service.dart
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_stripe/flutter_stripe.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class StripeService extends ChangeNotifier {
  static const String baseUrl = 'http://10.0.2.2:8000/api'; // Android Emulator
  // static const String baseUrl = 'http://localhost:8000/api'; // iOS Simulator
  
  bool _isLoading = false;
  String? _lastPaymentIntentId;
  
  bool get isLoading => _isLoading;
  String? get lastPaymentIntentId => _lastPaymentIntentId;
  
  Future<String?> _getAuthToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('auth_token');
  }
  
  Future<Map<String, String>> _getHeaders() async {
    final token = await _getAuthToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }
  
  // Crear Payment Intent
  Future<PaymentSheet?> createPaymentSheet({
    required double amount,
    required String description,
  }) async {
    try {
      _isLoading = true;
      notifyListeners();
      
      final headers = await _getHeaders();
      final response = await http.post(
        Uri.parse('$baseUrl/finanzas/stripe/payment-intent/'),
        headers: headers,
        body: jsonEncode({
          'amount': (amount * 100).round(), // Convertir a centavos
          'description': description,
        }),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _lastPaymentIntentId = data['payment_intent_id'];
        
        // Configurar Payment Sheet
        await Stripe.instance.initPaymentSheet(
          paymentSheetParameters: SetupPaymentSheetParameters(
            paymentIntentClientSecret: data['client_secret'],
            merchantDisplayName: 'Condominio App',
            style: ThemeMode.system,
          ),
        );
        
        return PaymentSheet();
      } else {
        throw Exception('Error creando Payment Intent: ${response.body}');
      }
    } catch (e) {
      print('Error en createPaymentSheet: $e');
      return null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  // Procesar pago
  Future<bool> processPayment() async {
    try {
      await Stripe.instance.presentPaymentSheet();
      return true;
    } on StripeException catch (e) {
      print('Error procesando pago: $e');
      return false;
    }
  }
  
  // Guardar método de pago
  Future<SetupIntent?> setupPaymentMethod() async {
    try {
      _isLoading = true;
      notifyListeners();
      
      final headers = await _getHeaders();
      final response = await http.post(
        Uri.parse('$baseUrl/finanzas/stripe/setup-intent/'),
        headers: headers,
        body: jsonEncode({}),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        
        await Stripe.instance.initPaymentSheet(
          paymentSheetParameters: SetupPaymentSheetParameters(
            setupIntentClientSecret: data['client_secret'],
            merchantDisplayName: 'Condominio App',
            style: ThemeMode.system,
          ),
        );
        
        await Stripe.instance.presentPaymentSheet();
        
        return SetupIntent();
      } else {
        throw Exception('Error creando Setup Intent: ${response.body}');
      }
    } catch (e) {
      print('Error en setupPaymentMethod: $e');
      return null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  // Verificar estado de pago
  Future<String?> getPaymentStatus(String paymentIntentId) async {
    try {
      final headers = await _getHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/finanzas/stripe/payment-status/$paymentIntentId/'),
        headers: headers,
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['status'];
      }
      return null;
    } catch (e) {
      print('Error verificando estado: $e');
      return null;
    }
  }
}
```

### 4. Pantalla de Pagos - payment_screen.dart
```dart
// lib/screens/payment_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fluttertoast/fluttertoast.dart';
import '../services/stripe_service.dart';

class PaymentScreen extends StatefulWidget {
  @override
  _PaymentScreenState createState() => _PaymentScreenState();
}

class _PaymentScreenState extends State<PaymentScreen> {
  final _amountController = TextEditingController();
  final _descriptionController = TextEditingController();
  
  @override
  void dispose() {
    _amountController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }
  
  Future<void> _processPayment() async {
    final stripeService = Provider.of<StripeService>(context, listen: false);
    
    final amount = double.tryParse(_amountController.text);
    if (amount == null || amount <= 0) {
      _showToast('Ingresa un monto válido');
      return;
    }
    
    final description = _descriptionController.text.trim();
    if (description.isEmpty) {
      _showToast('Ingresa una descripción');
      return;
    }
    
    // Crear Payment Sheet
    final paymentSheet = await stripeService.createPaymentSheet(
      amount: amount,
      description: description,
    );
    
    if (paymentSheet != null) {
      // Procesar pago
      final success = await stripeService.processPayment();
      if (success) {
        _showToast('¡Pago realizado exitosamente!');
        _clearForm();
      } else {
        _showToast('Error procesando el pago');
      }
    } else {
      _showToast('Error preparando el pago');
    }
  }
  
  Future<void> _savePaymentMethod() async {
    final stripeService = Provider.of<StripeService>(context, listen: false);
    
    final setupIntent = await stripeService.setupPaymentMethod();
    if (setupIntent != null) {
      _showToast('Método de pago guardado exitosamente');
    } else {
      _showToast('Error guardando método de pago');
    }
  }
  
  void _showToast(String message) {
    Fluttertoast.showToast(
      msg: message,
      toastLength: Toast.LENGTH_SHORT,
      gravity: ToastGravity.BOTTOM,
    );
  }
  
  void _clearForm() {
    _amountController.clear();
    _descriptionController.clear();
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Pagos con Stripe'),
        backgroundColor: Colors.blue,
      ),
      body: Consumer<StripeService>(
        builder: (context, stripeService, child) {
          return Padding(
            padding: EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Título
                Card(
                  child: Padding(
                    padding: EdgeInsets.all(16.0),
                    child: Column(
                      children: [
                        Icon(Icons.payment, size: 48, color: Colors.blue),
                        SizedBox(height: 8),
                        Text(
                          'Sistema de Pagos',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          'Procesa pagos de manera segura',
                          style: TextStyle(color: Colors.grey[600]),
                        ),
                      ],
                    ),
                  ),
                ),
                
                SizedBox(height: 20),
                
                // Formulario de pago
                TextField(
                  controller: _amountController,
                  keyboardType: TextInputType.numberWithOptions(decimal: true),
                  decoration: InputDecoration(
                    labelText: 'Monto a pagar',
                    prefixText: '\$',
                    border: OutlineInputBorder(),
                    hintText: 'Ej: 15.00',
                  ),
                ),
                
                SizedBox(height: 16),
                
                TextField(
                  controller: _descriptionController,
                  decoration: InputDecoration(
                    labelText: 'Descripción del pago',
                    border: OutlineInputBorder(),
                    hintText: 'Ej: Pago de mantenimiento',
                  ),
                  maxLines: 2,
                ),
                
                SizedBox(height: 24),
                
                // Botones de acción
                if (stripeService.isLoading)
                  Center(
                    child: Column(
                      children: [
                        CircularProgressIndicator(),
                        SizedBox(height: 8),
                        Text('Procesando...'),
                      ],
                    ),
                  )
                else
                  Column(
                    children: [
                      ElevatedButton.icon(
                        onPressed: _processPayment,
                        icon: Icon(Icons.payment),
                        label: Text('Pagar Ahora'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.green,
                          foregroundColor: Colors.white,
                          padding: EdgeInsets.symmetric(vertical: 16),
                          textStyle: TextStyle(fontSize: 16),
                        ),
                      ),
                      
                      SizedBox(height: 12),
                      
                      OutlinedButton.icon(
                        onPressed: _savePaymentMethod,
                        icon: Icon(Icons.save),
                        label: Text('Guardar Método de Pago'),
                        style: OutlinedButton.styleFrom(
                          padding: EdgeInsets.symmetric(vertical: 16),
                          textStyle: TextStyle(fontSize: 16),
                        ),
                      ),
                    ],
                  ),
                
                SizedBox(height: 20),
                
                // Estado del último pago
                if (stripeService.lastPaymentIntentId != null)
                  Card(
                    color: Colors.blue[50],
                    child: Padding(
                      padding: EdgeInsets.all(12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Último Pago:',
                            style: TextStyle(fontWeight: FontWeight.bold),
                          ),
                          Text(
                            'ID: ${stripeService.lastPaymentIntentId}',
                            style: TextStyle(
                              fontFamily: 'monospace',
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
              ],
            ),
          );
        },
      ),
    );
  }
}
```

### 5. Servicio de Autenticación - auth_service.dart
```dart
// lib/services/auth_service.dart
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class AuthService extends ChangeNotifier {
  static const String baseUrl = 'http://10.0.2.2:8000/api';
  
  bool _isAuthenticated = false;
  String? _token;
  Map<String, dynamic>? _user;
  
  bool get isAuthenticated => _isAuthenticated;
  String? get token => _token;
  Map<String, dynamic>? get user => _user;
  
  Future<void> initialize() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('auth_token');
    if (_token != null) {
      _isAuthenticated = true;
      // Cargar datos del usuario si es necesario
      await _loadUserProfile();
    }
    notifyListeners();
  }
  
  Future<bool> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/token/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': username,
          'password': password,
        }),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _token = data['access'];
        _isAuthenticated = true;
        
        // Guardar token
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('auth_token', _token!);
        
        await _loadUserProfile();
        notifyListeners();
        return true;
      }
      return false;
    } catch (e) {
      print('Error login: $e');
      return false;
    }
  }
  
  Future<void> _loadUserProfile() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/usuarios/perfil/'),
        headers: {
          'Authorization': 'Bearer $_token',
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        _user = jsonDecode(response.body);
        notifyListeners();
      }
    } catch (e) {
      print('Error loading profile: $e');
    }
  }
  
  Future<void> logout() async {
    _token = null;
    _isAuthenticated = false;
    _user = null;
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
    
    notifyListeners();
  }
}
```

---

## 🧪 Testing y Debugging

### 1. Script de Prueba Backend
```bash
# Ejecutar script de prueba
cd c:\Users\asus\Documents\desplegable\backendd
python test_stripe_integration.py
```

### 2. Tarjetas de Prueba Stripe
```dart
// Para testing en modo desarrollo, usa estas tarjetas:

// Visa - Pago exitoso
4242424242424242

// Visa - Pago fallido
4000000000000002

// Mastercard - Pago exitoso
5555555555554444

// American Express - Pago exitoso
378282246310005

// CVV: cualquier 3-4 dígitos
// Fecha: cualquier fecha futura
// ZIP: cualquier código postal
```

### 3. Debug en Flutter
```dart
// Añadir logs en stripe_service.dart
print('Response status: ${response.statusCode}');
print('Response body: ${response.body}');

// Verificar headers
final headers = await _getHeaders();
print('Headers: $headers');
```

---

## 🚀 Producción y Deploy

### 1. Variables de Entorno Producción
```bash
# En tu servidor de producción
export STRIPE_PUBLISHABLE_KEY="pk_live_xxxxxx"
export STRIPE_SECRET_KEY="sk_live_xxxxxx"
export STRIPE_WEBHOOK_SECRET="whsec_xxxxxx"
export DEBUG="False"
```

### 2. Configuración Flutter Producción
```dart
// lib/config/constants.dart
class Config {
  static const String baseUrl = 'https://tu-dominio.com/api';
  static const String stripePublishableKey = 'pk_live_tu_clave_real';
}
```

### 3. Webhook en Producción
```bash
# En Stripe Dashboard:
# 1. Cambiar a Live Mode
# 2. Configurar webhook: https://tu-dominio.com/api/finanzas/stripe/webhook/
# 3. Actualizar STRIPE_WEBHOOK_SECRET en el servidor
```

---

## 🐛 Troubleshooting

### Errores Comunes

#### 1. "No module named 'stripe'"
```bash
# Solución:
pip install stripe==13.0.0
```

#### 2. "Invalid publishable key"
```dart
// Verificar que la clave sea correcta en main.dart
Stripe.publishableKey = "pk_test_tu_clave_correcta";
```

#### 3. "Network request failed"
```dart
// Verificar URL en Android Emulator
static const String baseUrl = 'http://10.0.2.2:8000/api';

// Para dispositivo físico, usar IP real:
static const String baseUrl = 'http://192.168.x.x:8000/api';
```

#### 4. "401 Unauthorized"
```dart
// Verificar token en SharedPreferences
final prefs = await SharedPreferences.getInstance();
final token = prefs.getString('auth_token');
print('Token: $token');
```

#### 5. "Webhook signature verification failed"
```python
# Verificar STRIPE_WEBHOOK_SECRET en settings.py
print(f"Webhook secret: {settings.STRIPE_WEBHOOK_SECRET}")
```

### Debug Commands
```bash
# Ver logs del servidor Django
python manage.py runserver --verbosity=2

# Ver migraciones pendientes
python manage.py showmigrations

# Verificar configuración
python manage.py shell
>>> from django.conf import settings
>>> print(settings.STRIPE_SECRET_KEY)
```

---

## ✅ Checklist Final

### Backend ✅
- [x] Stripe service implementado
- [x] API views creadas
- [x] URLs configuradas
- [x] Migraciones aplicadas
- [x] Variables de entorno configuradas

### Flutter 📱
- [ ] Dependencias añadidas
- [ ] StripeService implementado
- [ ] Pantallas de pago creadas
- [ ] AuthService configurado
- [ ] Testing en dispositivo

### Stripe Dashboard 💳
- [ ] Cuenta creada
- [ ] Claves API obtenidas
- [ ] Webhook configurado
- [ ] Eventos seleccionados

### Testing 🧪
- [ ] Backend endpoints probados
- [ ] Pagos test realizados
- [ ] Webhook verificado
- [ ] Errores manejados

---

## 🎯 Próximos Pasos

1. **Implementar el código Flutter** usando los ejemplos de arriba
2. **Configurar las claves de Stripe** en el archivo .env
3. **Probar pagos** con las tarjetas de prueba
4. **Configurar webhook** en Stripe Dashboard
5. **Deploy a producción** cuando esté todo funcionando

¡Con esta guía tienes todo lo necesario para implementar un sistema completo de pagos móvil con Stripe! 🚀