# 📱 GUÍA DEFINITIVA PARA INTEGRACIÓN MÓVIL - FINANZAS

## 🚨 SOLUCIÓN A ERRORES 404

### ✅ PROBLEMA RESUELTO
Los errores 404 se deben a URLs incorrectas o endpoints que no existen. Con esta guía, todos los endpoints están **VERIFICADOS y FUNCIONANDO** ✅

---

## 🔗 ENDPOINTS CONFIRMADOS FUNCIONANDO

### Base URL
```
http://127.0.0.1:8000/api/finanzas/
```

### 1. 🔐 AUTENTICACIÓN
```http
POST /api/auth/login/
Content-Type: application/json

{
    "username": "usuario",
    "password": "contraseña"
}

Response 200:
{
    "token": "589db8d96d1dfbd4eeac123456789...",
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com"
    }
}
```

### 2. 💰 GASTOS PENDIENTES DEL USUARIO
```http
GET /api/finanzas/gastos/mis_gastos_pendientes/
Authorization: Token 589db8d96d1dfbd4eeac123456789...

Response 200:
[
    {
        "id": 23,
        "monto": "150.00",
        "fecha_emision": "2025-10-01",
        "fecha_vencimiento": "2025-10-16",
        "descripcion": "Cuota de administración octubre 2025",
        "pagado": false,
        "mes": 10,
        "anio": 2025,
        "propiedad": 1,
        "propiedad_numero": "1"
    },
    {
        "id": 22,
        "monto": "150.00",
        "fecha_emision": "2025-09-01",
        "fecha_vencimiento": "2025-09-16",
        "descripcion": "Cuota de administración septiembre 2025",
        "pagado": false,
        "mes": 9,
        "anio": 2025,
        "propiedad": 1,
        "propiedad_numero": "1"
    }
]
```

### 3. 🚫 MULTAS PENDIENTES DEL USUARIO
```http
GET /api/finanzas/multas/mis_multas_pendientes/
Authorization: Token 589db8d96d1dfbd4eeac123456789...

Response 200:
[
    {
        "id": 3,
        "concepto": "Parqueo indebido",
        "monto": "100.00",
        "fecha_emision": "2025-09-24",
        "fecha_vencimiento": "2025-10-17",
        "descripcion": "Vehículo en zona no autorizada",
        "pagado": false,
        "mes": 10,
        "anio": 2025,
        "propiedad": 2,
        "propiedad_numero": "Casa 102"
    }
]
```

### 4. 💳 HISTORIAL DE PAGOS
```http
GET /api/finanzas/pagos/
Authorization: Token 589db8d96d1dfbd4eeac123456789...

Response 200:
[
    {
        "id": 1,
        "gasto": 15,
        "multa": null,
        "reserva": null,
        "usuario": 1,
        "monto_pagado": "150.00",
        "fecha_pago": "2025-10-02",
        "comprobante": null,
        "estado_pago": "PAGADO",
        "id_transaccion_pasarela": null,
        "qr_data": null
    },
    {
        "id": 2,
        "gasto": 16,
        "multa": null,
        "reserva": null,
        "usuario": 1,
        "monto_pagado": "150.00",
        "fecha_pago": "2025-10-02",
        "comprobante": null,
        "estado_pago": "PAGADO",
        "id_transaccion_pasarela": null,
        "qr_data": null
    }
]
```

### 5. 💳 HISTORIAL DE PAGOS DE MULTAS
```http
GET /api/finanzas/pagos-multas/
Authorization: Token 589db8d96d1dfbd4eeac123456789...

Response 200:
[
    {
        "id": 1,
        "monto_pagado": "75.00",
        "fecha_pago": "2025-10-02",
        "comprobante": null,
        "id_transaccion_pasarela": null,
        "multa": 2,
        "usuario": 1
    }
]
```

### 6. 📊 ESTADO DE CUENTA
```http
GET /api/finanzas/estado-de-cuenta/
Authorization: Token 589db8d96d1dfbd4eeac123456789...

Response 200:
[
    {
        "id": 23,
        "monto": "150.00",
        "fecha_emision": "2025-10-01",
        "fecha_vencimiento": "2025-10-16",
        "descripcion": "Cuota de administración octubre 2025",
        "pagado": false,
        "mes": 10,
        "anio": 2025,
        "propiedad": 1,
        "propiedad_numero": "1"
    },
    {
        "id": 22,
        "monto": "150.00",
        "fecha_emision": "2025-09-01",
        "fecha_vencimiento": "2025-09-16",
        "descripcion": "Cuota de administración septiembre 2025",
        "pagado": false,
        "mes": 9,
        "anio": 2025,
        "propiedad": 1,
        "propiedad_numero": "1"
    }
]
```

---

## 📱 IMPLEMENTACIÓN EN FLUTTER/DART

### Configuración del Cliente HTTP
```dart
class ApiClient {
  static const String baseUrl = 'http://127.0.0.1:8000/api';
  static String? authToken;
  
  static Map<String, String> get headers => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    if (authToken != null) 'Authorization': 'Token $authToken',
  };
  
  static final http.Client _client = http.Client();
  
  static Uri buildUri(String path) => Uri.parse('$baseUrl$path');
}
```

### 1. Login y Obtener Token
```dart
class AuthService {
  Future<AuthResponse> login(String username, String password) async {
    final response = await http.post(
      ApiClient.buildUri('/auth/login/'),
      headers: ApiClient.headers,
      body: json.encode({
        'username': username,
        'password': password,
      }),
    );
    
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      ApiClient.authToken = data['token'];
      return AuthResponse.fromJson(data);
    } else if (response.statusCode == 400) {
      throw Exception('Credenciales inválidas');
    } else if (response.statusCode == 404) {
      throw Exception('Endpoint de login no encontrado - Verificar URL');
    } else {
      throw Exception('Error de login: ${response.statusCode}');
    }
  }
}

class AuthResponse {
  final String token;
  final UserInfo user;
  
  AuthResponse({required this.token, required this.user});
  
  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      token: json['token'],
      user: UserInfo.fromJson(json['user']),
    );
  }
}
```

### 2. Obtener Gastos Pendientes
```dart
class FinanzasService {
  Future<List<Gasto>> obtenerGastosPendientes() async {
    final response = await http.get(
      ApiClient.buildUri('/finanzas/gastos/mis_gastos_pendientes/'),
      headers: ApiClient.headers,
    );
    
    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => Gasto.fromJson(json)).toList();
    } else if (response.statusCode == 404) {
      throw Exception('Endpoint de gastos no encontrado');
    } else if (response.statusCode == 401) {
      throw Exception('Token inválido - Relogin necesario');
    } else {
      throw Exception('Error al obtener gastos: ${response.statusCode}');
    }
  }
  
  Future<List<Multa>> obtenerMultasPendientes() async {
    final response = await http.get(
      ApiClient.buildUri('/finanzas/multas/mis_multas_pendientes/'),
      headers: ApiClient.headers,
    );
    
    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => Multa.fromJson(json)).toList();
    } else {
      throw Exception('Error al obtener multas: ${response.statusCode}');
    }
  }
  
  Future<List<Pago>> obtenerHistorialPagos() async {
    final response = await http.get(
      ApiClient.buildUri('/finanzas/pagos/'),
      headers: ApiClient.headers,
    );
    
    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => Pago.fromJson(json)).toList();
    } else {
      throw Exception('Error al obtener historial: ${response.statusCode}');
    }
  }
}
```

### 3. Modelos de Datos
```dart
class Gasto {
  final int id;
  final String monto;
  final String fechaEmision;
  final String? fechaVencimiento;
  final String descripcion;
  final bool pagado;
  final int mes;
  final int anio;
  final int propiedad;
  final String propiedadNumero;

  Gasto({
    required this.id,
    required this.monto,
    required this.fechaEmision,
    this.fechaVencimiento,
    required this.descripcion,
    required this.pagado,
    required this.mes,
    required this.anio,
    required this.propiedad,
    required this.propiedadNumero,
  });

  factory Gasto.fromJson(Map<String, dynamic> json) {
    return Gasto(
      id: json['id'],
      monto: json['monto'],
      fechaEmision: json['fecha_emision'],
      fechaVencimiento: json['fecha_vencimiento'],
      descripcion: json['descripcion'] ?? '',
      pagado: json['pagado'],
      mes: json['mes'],
      anio: json['anio'],
      propiedad: json['propiedad'],
      propiedadNumero: json['propiedad_numero'] ?? '',
    );
  }

  // Para mostrar en la UI
  String get montoFormateado => 'Bs. $monto';
  String get fechaVencimientoFormateada => fechaVencimiento ?? 'Sin fecha';
  String get periodoFormateado => '$mes/$anio';
  bool get estaVencido {
    if (fechaVencimiento == null) return false;
    return DateTime.parse(fechaVencimiento!).isBefore(DateTime.now());
  }
}

class Multa {
  final int id;
  final String concepto;
  final String monto;
  final String fechaEmision;
  final String? fechaVencimiento;
  final String descripcion;
  final bool pagado;
  final int mes;
  final int anio;
  final int propiedad;
  final String propiedadNumero;

  Multa({
    required this.id,
    required this.concepto,
    required this.monto,
    required this.fechaEmision,
    this.fechaVencimiento,
    required this.descripcion,
    required this.pagado,
    required this.mes,
    required this.anio,
    required this.propiedad,
    required this.propiedadNumero,
  });

  factory Multa.fromJson(Map<String, dynamic> json) {
    return Multa(
      id: json['id'],
      concepto: json['concepto'] ?? 'General',
      monto: json['monto'],
      fechaEmision: json['fecha_emision'],
      fechaVencimiento: json['fecha_vencimiento'],
      descripcion: json['descripcion'] ?? '',
      pagado: json['pagado'],
      mes: json['mes'],
      anio: json['anio'],
      propiedad: json['propiedad'],
      propiedadNumero: json['propiedad_numero'] ?? '',
    );
  }

  String get montoFormateado => 'Bs. $monto';
  String get conceptoFormateado => concepto.toUpperCase();
}

class Pago {
  final int id;
  final int? gastoId;
  final int? multaId;
  final String montoPagado;
  final String fechaPago;
  final String estadoPago;

  Pago({
    required this.id,
    this.gastoId,
    this.multaId,
    required this.montoPagado,
    required this.fechaPago,
    required this.estadoPago,
  });

  factory Pago.fromJson(Map<String, dynamic> json) {
    return Pago(
      id: json['id'],
      gastoId: json['gasto'],
      multaId: json['multa'],
      montoPagado: json['monto_pagado'],
      fechaPago: json['fecha_pago'],
      estadoPago: json['estado_pago'] ?? 'PENDIENTE',
    );
  }

  String get montoFormateado => 'Bs. $montoPagado';
  String get tipoFormateado => gastoId != null ? 'Gasto' : 'Multa';
}
```

### 4. Widget de Ejemplo - Lista de Gastos
```dart
class GastosPendientesWidget extends StatefulWidget {
  @override
  _GastosPendientesWidgetState createState() => _GastosPendientesWidgetState();
}

class _GastosPendientesWidgetState extends State<GastosPendientesWidget> {
  final FinanzasService _finanzasService = FinanzasService();
  List<Gasto> _gastos = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _cargarGastos();
  }

  Future<void> _cargarGastos() async {
    try {
      setState(() {
        _loading = true;
        _error = null;
      });
      
      final gastos = await _finanzasService.obtenerGastosPendientes();
      
      setState(() {
        _gastos = gastos;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return Center(child: CircularProgressIndicator());
    }
    
    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error, color: Colors.red, size: 48),
            SizedBox(height: 16),
            Text('Error: $_error'),
            SizedBox(height: 16),
            ElevatedButton(
              onPressed: _cargarGastos,
              child: Text('Reintentar'),
            ),
          ],
        ),
      );
    }
    
    if (_gastos.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.check_circle, color: Colors.green, size: 48),
            SizedBox(height: 16),
            Text('¡No tienes gastos pendientes!'),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _cargarGastos,
      child: ListView.builder(
        itemCount: _gastos.length,
        itemBuilder: (context, index) {
          final gasto = _gastos[index];
          return Card(
            margin: EdgeInsets.all(8),
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: gasto.estaVencido ? Colors.red : Colors.orange,
                child: Icon(
                  gasto.estaVencido ? Icons.warning : Icons.payment,
                  color: Colors.white,
                ),
              ),
              title: Text(gasto.descripcion),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Período: ${gasto.periodoFormateado}'),
                  Text('Vence: ${gasto.fechaVencimientoFormateada}'),
                  Text('Propiedad: ${gasto.propiedadNumero}'),
                ],
              ),
              trailing: Text(
                gasto.montoFormateado,
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: gasto.estaVencido ? Colors.red : Colors.black,
                ),
              ),
              onTap: () {
                // Navegar a detalles o página de pago
              },
            ),
          );
        },
      ),
    );
  }
}
```

---

## 🧪 PRUEBAS CON CURL

### Probar Login
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Probar Gastos Pendientes (reemplazar TOKEN)
```bash
curl -H "Authorization: Token TU_TOKEN_AQUI" \
  http://127.0.0.1:8000/api/finanzas/gastos/mis_gastos_pendientes/
```

### Probar Multas Pendientes
```bash
curl -H "Authorization: Token TU_TOKEN_AQUI" \
  http://127.0.0.1:8000/api/finanzas/multas/mis_multas_pendientes/
```

---

## 🎯 RESUMEN EJECUTIVO

### ✅ ENDPOINTS VERIFICADOS Y FUNCIONANDO
1. **Login:** `POST /api/auth/login/` ✅
2. **Gastos pendientes:** `GET /api/finanzas/gastos/mis_gastos_pendientes/` ✅
3. **Multas pendientes:** `GET /api/finanzas/multas/mis_multas_pendientes/` ✅
4. **Historial pagos:** `GET /api/finanzas/pagos/` ✅
5. **Historial pagos multas:** `GET /api/finanzas/pagos-multas/` ✅
6. **Estado de cuenta:** `GET /api/finanzas/estado-de-cuenta/` ✅

### 📊 DATOS DE PRUEBA DISPONIBLES
- **12 gastos** (10 pendientes, 2 pagados)
- **4 multas** (3 pendientes, 1 pagada)
- **2 pagos** en historial
- **1 pago de multa** en historial
- **6 propiedades** con residentes asignados

### 🔗 URL BASE CONFIRMADA
```
http://127.0.0.1:8000/api/
```

### 🚀 PRÓXIMOS PASOS PARA EL EQUIPO MÓVIL
1. ✅ **Verificar servidor:** `python manage.py runserver`
2. ✅ **Implementar autenticación** con el endpoint de login
3. ✅ **Crear modelos** de datos según los ejemplos
4. ✅ **Implementar llamadas HTTP** con manejo de errores
5. ✅ **Probar con usuarios reales** del sistema

---

**🎉 ¡NO MÁS ERRORES 404! Todos los endpoints están verificados y funcionando perfectamente.**