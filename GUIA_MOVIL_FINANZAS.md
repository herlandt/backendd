# 📱 GUÍA DE IMPLEMENTACIÓN MÓVIL - FINANZAS API

## 🚨 SOLUCIÓN A ERRORES 404

### 🔧 URLs Base Correctas
```
BASE_URL = "http://127.0.0.1:8000/api/"
FINANZAS_BASE = "http://127.0.0.1:8000/api/finanzas/"
```

## 📊 ENDPOINTS DISPONIBLES

### 1. 💰 GASTOS (Cuotas de Administración)
```http
GET    /api/finanzas/gastos/                    # Listar gastos del usuario
GET    /api/finanzas/gastos/{id}/               # Detalle de un gasto
POST   /api/finanzas/gastos/                    # Crear gasto (solo admin)
PUT    /api/finanzas/gastos/{id}/               # Editar gasto (solo admin)
DELETE /api/finanzas/gastos/{id}/               # Eliminar gasto (solo admin)

# Acciones especiales
GET    /api/finanzas/gastos/mis_gastos_pendientes/  # Gastos sin pagar del usuario
```

### 2. 🚫 MULTAS
```http
GET    /api/finanzas/multas/                    # Listar multas del usuario
GET    /api/finanzas/multas/{id}/               # Detalle de una multa
POST   /api/finanzas/multas/                    # Crear multa (solo admin)
PUT    /api/finanzas/multas/{id}/               # Editar multa (solo admin)
DELETE /api/finanzas/multas/{id}/               # Eliminar multa (solo admin)

# Acciones especiales
GET    /api/finanzas/multas/mis_multas_pendientes/  # Multas sin pagar del usuario
```

### 3. 💳 PAGOS (Historial de Pagos de Gastos)
```http
GET    /api/finanzas/pagos/                     # Historial de pagos del usuario
GET    /api/finanzas/pagos/{id}/                # Detalle de un pago
POST   /api/finanzas/pagos/                     # Registrar pago manual (solo admin)

# Comprobantes
GET    /api/finanzas/pagos/{id}/comprobante/    # Descargar PDF del comprobante
```

### 4. 💳 PAGOS DE MULTAS (Historial de Pagos de Multas)
```http
GET    /api/finanzas/pagos-multas/              # Historial de pagos de multas
GET    /api/finanzas/pagos-multas/{id}/         # Detalle de un pago de multa
POST   /api/finanzas/pagos-multas/              # Registrar pago de multa (solo admin)

# Comprobantes
GET    /api/finanzas/pagos-multas/{id}/comprobante/  # Descargar PDF del comprobante
```

### 5. 🏢 RESERVAS DE ÁREAS COMUNES
```http
GET    /api/finanzas/reservas/                  # Reservas del usuario
GET    /api/finanzas/reservas/{id}/             # Detalle de una reserva
POST   /api/finanzas/reservas/                  # Crear nueva reserva
PUT    /api/finanzas/reservas/{id}/             # Editar reserva
DELETE /api/finanzas/reservas/{id}/             # Cancelar reserva

# Pagos de reservas
POST   /api/finanzas/reservas/{id}/pagar/       # Pagar una reserva
```

### 6. 📊 REPORTES Y ESTADO DE CUENTA
```http
GET    /api/finanzas/estado-de-cuenta/          # Estado de cuenta del usuario
GET    /api/finanzas/reportes/resumen/          # Resumen financiero
GET    /api/finanzas/reportes/estado-morosidad/ # Reporte de morosidad (solo admin)
```

## 🔐 AUTENTICACIÓN REQUERIDA

### Headers Obligatorios
```http
Authorization: Token YOUR_TOKEN_HERE
Content-Type: application/json
```

### Obtener Token
```http
POST /api/auth/login/
{
    "username": "usuario",
    "password": "contraseña"
}

Response:
{
    "token": "abc123def456...",
    "user": {
        "id": 1,
        "username": "usuario",
        "email": "email@example.com"
    }
}
```

## 📱 EJEMPLOS DE IMPLEMENTACIÓN MÓVIL

### 1. 💰 Obtener Gastos Pendientes
```dart
// Flutter/Dart
Future<List<Gasto>> obtenerGastosPendientes() async {
  final response = await http.get(
    Uri.parse('$baseUrl/api/finanzas/gastos/mis_gastos_pendientes/'),
    headers: {
      'Authorization': 'Token $token',
      'Content-Type': 'application/json',
    },
  );
  
  if (response.statusCode == 200) {
    final List<dynamic> data = json.decode(response.body);
    return data.map((json) => Gasto.fromJson(json)).toList();
  } else if (response.statusCode == 404) {
    throw Exception('Endpoint no encontrado - Verificar URL');
  } else {
    throw Exception('Error ${response.statusCode}: ${response.body}');
  }
}
```

### 2. 🚫 Obtener Multas Pendientes
```dart
Future<List<Multa>> obtenerMultasPendientes() async {
  final response = await http.get(
    Uri.parse('$baseUrl/api/finanzas/multas/mis_multas_pendientes/'),
    headers: {
      'Authorization': 'Token $token',
      'Content-Type': 'application/json',
    },
  );
  
  if (response.statusCode == 200) {
    final List<dynamic> data = json.decode(response.body);
    return data.map((json) => Multa.fromJson(json)).toList();
  } else {
    throw Exception('Error ${response.statusCode}: ${response.body}');
  }
}
```

### 3. 📊 Obtener Estado de Cuenta
```dart
Future<EstadoCuenta> obtenerEstadoCuenta() async {
  final response = await http.get(
    Uri.parse('$baseUrl/api/finanzas/estado-de-cuenta/'),
    headers: {
      'Authorization': 'Token $token',
      'Content-Type': 'application/json',
    },
  );
  
  if (response.statusCode == 200) {
    return EstadoCuenta.fromJson(json.decode(response.body));
  } else {
    throw Exception('Error ${response.statusCode}: ${response.body}');
  }
}
```

### 4. 💳 Obtener Historial de Pagos
```dart
Future<List<Pago>> obtenerHistorialPagos() async {
  final response = await http.get(
    Uri.parse('$baseUrl/api/finanzas/pagos/'),
    headers: {
      'Authorization': 'Token $token',
      'Content-Type': 'application/json',
    },
  );
  
  if (response.statusCode == 200) {
    final List<dynamic> data = json.decode(response.body);
    return data.map((json) => Pago.fromJson(json)).toList();
  } else {
    throw Exception('Error ${response.statusCode}: ${response.body}');
  }
}
```

## 📋 MODELOS DE DATOS SUGERIDOS

### Gasto Model
```dart
class Gasto {
  final int id;
  final int propiedadId;
  final String propiedadNumero;
  final double monto;
  final String fechaEmision;
  final String? fechaVencimiento;
  final String descripcion;
  final bool pagado;
  final int mes;
  final int anio;

  Gasto({
    required this.id,
    required this.propiedadId,
    required this.propiedadNumero,
    required this.monto,
    required this.fechaEmision,
    this.fechaVencimiento,
    required this.descripcion,
    required this.pagado,
    required this.mes,
    required this.anio,
  });

  factory Gasto.fromJson(Map<String, dynamic> json) {
    return Gasto(
      id: json['id'],
      propiedadId: json['propiedad'],
      propiedadNumero: json['propiedad_numero'] ?? '',
      monto: double.parse(json['monto'].toString()),
      fechaEmision: json['fecha_emision'],
      fechaVencimiento: json['fecha_vencimiento'],
      descripcion: json['descripcion'] ?? '',
      pagado: json['pagado'],
      mes: json['mes'],
      anio: json['anio'],
    );
  }
}
```

### Multa Model
```dart
class Multa {
  final int id;
  final int propiedadId;
  final String propiedadNumero;
  final String concepto;
  final double monto;
  final String fechaEmision;
  final String? fechaVencimiento;
  final String descripcion;
  final bool pagado;
  final int mes;
  final int anio;

  Multa({
    required this.id,
    required this.propiedadId,
    required this.propiedadNumero,
    required this.concepto,
    required this.monto,
    required this.fechaEmision,
    this.fechaVencimiento,
    required this.descripcion,
    required this.pagado,
    required this.mes,
    required this.anio,
  });

  factory Multa.fromJson(Map<String, dynamic> json) {
    return Multa(
      id: json['id'],
      propiedadId: json['propiedad'],
      propiedadNumero: json['propiedad_numero'] ?? '',
      concepto: json['concepto'] ?? 'General',
      monto: double.parse(json['monto'].toString()),
      fechaEmision: json['fecha_emision'],
      fechaVencimiento: json['fecha_vencimiento'],
      descripcion: json['descripcion'] ?? '',
      pagado: json['pagado'],
      mes: json['mes'],
      anio: json['anio'],
    );
  }
}
```

### Pago Model
```dart
class Pago {
  final int id;
  final int gastoId;
  final double monto;
  final String fechaPago;
  final String metodoPago;
  final String? numeroComprobante;
  final String? descripcion;

  Pago({
    required this.id,
    required this.gastoId,
    required this.monto,
    required this.fechaPago,
    required this.metodoPago,
    this.numeroComprobante,
    this.descripcion,
  });

  factory Pago.fromJson(Map<String, dynamic> json) {
    return Pago(
      id: json['id'],
      gastoId: json['gasto'],
      monto: double.parse(json['monto'].toString()),
      fechaPago: json['fecha_pago'],
      metodoPago: json['metodo_pago'],
      numeroComprobante: json['numero_comprobante'],
      descripcion: json['descripcion'],
    );
  }
}
```

## 🔍 FILTROS DISPONIBLES

### Gastos
```http
GET /api/finanzas/gastos/?pagado=false         # Solo gastos sin pagar
GET /api/finanzas/gastos/?mes=10&anio=2025     # Gastos de octubre 2025
GET /api/finanzas/gastos/?monto__gte=100       # Gastos >= 100
GET /api/finanzas/gastos/?fecha_emision__gte=2025-01-01  # Desde enero 2025
```

### Multas
```http
GET /api/finanzas/multas/?pagado=false         # Solo multas sin pagar
GET /api/finanzas/multas/?concepto=Ruido       # Multas por ruido
GET /api/finanzas/multas/?monto__lte=50        # Multas <= 50
```

### Pagos
```http
GET /api/finanzas/pagos/?metodo_pago=efectivo  # Solo pagos en efectivo
GET /api/finanzas/pagos/?fecha_pago__gte=2025-01-01  # Pagos desde enero
```

## 🚨 MANEJO DE ERRORES COMUNES

### Error 404 - Not Found
```dart
if (response.statusCode == 404) {
  // Verificar que la URL base sea correcta
  // Verificar que el endpoint exista
  // Verificar que el servidor esté corriendo
  throw Exception('Endpoint no encontrado - Verificar URL');
}
```

### Error 401 - No autorizado
```dart
if (response.statusCode == 401) {
  // Token expirado o inválido
  // Redirigir a login
  throw Exception('Token inválido - Relogin requerido');
}
```

### Error 403 - Prohibido
```dart
if (response.statusCode == 403) {
  // Usuario no tiene permisos
  // Verificar rol del usuario
  throw Exception('Sin permisos para esta acción');
}
```

## 🧪 TESTING CON CURL

### Probar Gastos
```bash
# Obtener gastos del usuario
curl -H "Authorization: Token YOUR_TOKEN" \
     http://127.0.0.1:8000/api/finanzas/gastos/

# Obtener gastos pendientes
curl -H "Authorization: Token YOUR_TOKEN" \
     http://127.0.0.1:8000/api/finanzas/gastos/mis_gastos_pendientes/
```

### Probar Multas
```bash
# Obtener multas del usuario
curl -H "Authorization: Token YOUR_TOKEN" \
     http://127.0.0.1:8000/api/finanzas/multas/

# Obtener multas pendientes
curl -H "Authorization: Token YOUR_TOKEN" \
     http://127.0.0.1:8000/api/finanzas/multas/mis_multas_pendientes/
```

### Probar Estado de Cuenta
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
     http://127.0.0.1:8000/api/finanzas/estado-de-cuenta/
```

## 📊 RESPUESTAS ESPERADAS

### Gastos Pendientes
```json
[
  {
    "id": 1,
    "propiedad": 1,
    "propiedad_numero": "Casa 101",
    "monto": "150.00",
    "fecha_emision": "2025-10-01",
    "fecha_vencimiento": "2025-10-15",
    "descripcion": "Cuota de administración octubre 2025",
    "pagado": false,
    "mes": 10,
    "anio": 2025
  }
]
```

### Estado de Cuenta
```json
{
  "resumen": {
    "total_gastos": "300.00",
    "total_pagado": "150.00",
    "total_pendiente": "150.00",
    "total_multas": "50.00",
    "multas_pagadas": "0.00",
    "multas_pendientes": "50.00"
  },
  "gastos_pendientes": [...],
  "multas_pendientes": [...],
  "ultimos_pagos": [...]
}
```

## 🛠️ CONFIGURACIÓN DEL CLIENTE HTTP

### Headers por defecto
```dart
class ApiClient {
  static const String baseUrl = 'http://127.0.0.1:8000';
  static String? token;
  
  static Map<String, String> get headers => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    if (token != null) 'Authorization': 'Token $token',
  };
  
  static Uri buildUri(String endpoint) {
    return Uri.parse('$baseUrl$endpoint');
  }
}
```

## 🎯 PRÓXIMOS PASOS

1. **✅ Verificar servidor corriendo:** `python manage.py runserver`
2. **✅ Probar endpoints con Postman/curl**
3. **✅ Implementar autenticación en la app**
4. **✅ Crear modelos de datos**
5. **✅ Implementar llamadas HTTP**
6. **✅ Manejar errores correctamente**
7. **✅ Probar con datos reales**

---

**🚀 Con esta guía, el equipo móvil debería poder integrar correctamente todos los endpoints de finanzas sin errores 404.**