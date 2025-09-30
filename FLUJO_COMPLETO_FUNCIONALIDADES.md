
# 🏢 FLUJO COMPLETO DE FUNCIONALIDADES - Sistema de Condominio

## 📋 ÍNDICE
1. [Arquitectura General](#arquitectura-general)
2. [Sistema de Autenticación y Usuarios](#sistema-de-autenticación-y-usuarios)
3. [Módulo Condominio](#módulo-condominio)
4. [Módulo Finanzas](#módulo-finanzas)
5. [Módulo Seguridad](#módulo-seguridad)
6. [Módulo Mantenimiento](#módulo-mantenimiento)
7. [Módulo Notificaciones](#módulo-notificaciones)
8. [Flujos de Integración](#flujos-de-integración)
9. [Diagrama de Arquitectura](#diagrama-de-arquitectura)

---

## 🏗️ ARQUITECTURA GENERAL

### Base URLs del Sistema
```
🌐 BASE URL: /api/
├── 🔐 Autenticación: /api/
├── 👥 Usuarios: /api/usuarios/
├── 🏠 Condominio: /api/condominio/
├── 💰 Finanzas: /api/finanzas/
├── 🛡️ Seguridad: /api/seguridad/
├── 🔧 Mantenimiento: /api/mantenimiento/
└── 📱 Notificaciones: /api/notificaciones/
```

### Sistema de Roles y Permisos
```
👤 ROLES DEL SISTEMA:
├── 🏢 PROPIETARIO (Admin total)
├── 🏡 RESIDENTE (Usuario normal)
├── 🛡️ SEGURIDAD (Personal de seguridad)
└── 🔧 MANTENIMIENTO (Personal técnico + especialidades)
```

---

## 🔐 SISTEMA DE AUTENTICACIÓN Y USUARIOS

### Endpoints de Autenticación
```
POST /api/login/
├── 📥 RECIBE: {"username": "user", "password": "pass"}
├── 📤 DEVUELVE: {"token": "abc123...", "user": {...}}
└── 🎯 FUNCIÓN: Autenticación con token DRF

POST /api/registro/
├── 📥 RECIBE: {"username": "user", "email": "...", "password": "..."}
├── 📤 DEVUELVE: Usuario creado + token
└── 🎯 FUNCIÓN: Registro público de nuevos usuarios
```

### Gestión de Usuarios (/api/usuarios/)
```
👥 RESIDENTES CRUD:
├── GET /residentes/ → Lista todos los residentes (Admin)
├── POST /residentes/ → Crear residente con propiedad
├── GET /residentes/{id}/ → Detalle de residente
├── PUT/PATCH /residentes/{id}/ → Actualizar residente
└── DELETE /residentes/{id}/ → Eliminar residente

📱 PERFIL Y DISPOSITIVOS:
├── GET /perfil/ → Perfil del usuario autenticado
├── POST /dispositivos/registrar/ → Registrar dispositivo móvil
├── POST /reconocimiento/registrar-rostro/ → Subir foto facial (AWS)
└── POST /setup/crear-primer-admin/ → Setup inicial del sistema
```

### Modelos de Usuario
```
🗄️ ESTRUCTURA DE DATOS:
User (Django built-in)
├── username, email, password
├── first_name, last_name
└── is_staff, is_active

UserProfile
├── user → User (OneToOne)
├── role → PROPIETARIO/RESIDENTE/SEGURIDAD/MANTENIMIENTO
└── especialidad → Solo para MANTENIMIENTO

Residente (Compatibilidad)
├── usuario → User (OneToOne)
├── propiedad → Propiedad (FK)
├── rol → propietario/inquilino/otro
└── face_id_aws → ID facial AWS
```

---

## 🏠 MÓDULO CONDOMINIO

### Base: /api/condominio/

```
🏠 PROPIEDADES:
GET/POST /propiedades/
├── 📥 FILTROS: numero_casa, metros_cuadrados, propietario
├── 📤 CAMPOS: numero_casa, propietario, metros_cuadrados
└── 🎯 FUNCIÓN: Gestión de unidades habitacionales

🌳 ÁREAS COMUNES:
GET /areas-comunes/
├── 📥 FILTROS: nombre, capacidad, costo_reserva
├── 📤 CAMPOS: nombre, descripcion, capacidad, costo_reserva, horarios
└── 🎯 FUNCIÓN: Espacios compartidos (piscina, salón, etc.)

📢 AVISOS:
GET/POST/PUT/DELETE /avisos/
├── 📥 FILTROS: titulo, fecha_publicacion
├── 📤 CAMPOS: titulo, contenido, fecha_publicacion
└── 🎯 FUNCIÓN: Comunicados del condominio

📋 REGLAS:
GET /reglas/
├── 📥 FILTROS: categoria, activa, codigo
├── 📤 CAMPOS: codigo, titulo, descripcion, categoria
└── 🎯 FUNCIÓN: Normativas del condominio (solo lectura)
```

### Filtros Avanzados Disponibles:
```
?numero_casa__icontains=101&metros_cuadrados__gte=80
?nombre__icontains=piscina&capacidad__gte=10
?categoria=SEGURIDAD&activa=true
```

---

## 💰 MÓDULO FINANZAS

### Base: /api/finanzas/

```
💳 GASTOS COMUNES:
GET/POST/PUT/DELETE /gastos/
├── 📥 FILTROS: mes, ano, categoria, monto, pagado, fecha_vencimiento
├── 📤 CAMPOS: concepto, monto, propiedad, categoria, mes, ano, pagado
├── 🔧 ACCIONES ESPECIALES:
│   ├── POST /gastos/registrar_pago/ → Pagar gasto individual
│   ├── POST /gastos/pagar_en_lote/ → Pagar múltiples gastos
│   └── POST /gastos/crear_mensual/ → Crear gastos recurrentes
└── 🎯 FUNCIÓN: Administración de expensas comunes

🚨 MULTAS:
GET/POST/PUT/DELETE /multas/
├── 📥 FILTROS: usuario, pagada, monto, fecha_multa
├── 📤 CAMPOS: usuario, concepto, monto, fecha_multa, pagada
├── 🔧 ACCIONES: POST /multas/pagar_en_lote/
└── 🎯 FUNCIÓN: Sanciones por infracciones

💰 PAGOS:
GET/POST /pagos/
├── 📥 FILTROS: usuario, monto, fecha_pago, metodo_pago, gasto, multa
├── 📤 CAMPOS: gasto/multa/reserva, monto_pagado, metodo_pago
└── 🎯 FUNCIÓN: Registro de pagos realizados

🎫 RESERVAS:
GET/POST/PUT/DELETE /reservas/
├── 📥 FILTROS: area_comun, usuario, fecha_reserva, pagada, costo_total
├── 📤 CAMPOS: area_comun, usuario, fecha_reserva, hora_inicio/fin, costo
├── 🔧 ACCIONES: POST /reservas/{id}/pagar/ → Pagar reserva
└── 🎯 FUNCIÓN: Reservas de áreas comunes

📊 CONTABILIDAD:
├── GET/POST /egresos/ → Gastos del condominio
├── GET/POST /ingresos/ → Ingresos del condominio
└── 🎯 FUNCIÓN: Contabilidad administrativa
```

### Reportes y Utilidades:
```
📈 REPORTES:
├── GET /reportes/estado-morosidad/ → Listado de morosos
├── GET /reportes/resumen/ → Resumen financiero
├── GET /reportes/financiero/ → Reporte detallado PDF
└── GET /reportes/uso-areas-comunes/ → Estadísticas de uso

🧾 COMPROBANTES:
├── GET /pagos/{id}/comprobante/ → PDF de comprobante
└── GET /pagos-multas/{id}/comprobante/ → PDF multa

⚙️ UTILIDADES:
├── POST /expensas/generar/ → Generar gastos automáticos
├── GET /estado-de-cuenta/ → Estado cuenta usuario
└── POST /webhook/pagosnet/ → Webhook pasarela de pagos
```

### Integración con Pasarela de Pagos:
```
💳 FLUJO DE PAGO:
1. POST /pagos/{id}/simular/ → Simular pago (demo)
2. Webhook → /webhook/pagosnet/ → Confirmación automática
3. Estado actualizado → Pago confirmado
```

---

## 🛡️ MÓDULO SEGURIDAD

### Base: /api/seguridad/

```
👥 VISITANTES:
GET/POST/PUT/DELETE /visitantes/
├── 📥 FILTROS: nombre, cedula, telefono
├── 📤 CAMPOS: nombre_completo, documento, telefono, email
└── 🎯 FUNCIÓN: Registro de personas externas

🚗 VEHÍCULOS:
GET/POST/PUT/DELETE /vehiculos/
├── 📥 FILTROS: placa, modelo, color, propiedad, tipo
├── 📤 CAMPOS: placa, modelo, color, propiedad/visitante
└── 🎯 FUNCIÓN: Registro vehicular (residentes + visitantes)

🚪 VISITAS:
GET/POST/PUT/DELETE /visitas/
├── 📥 FILTROS: propiedad, visitante, fechas, estado, ingresos/salidas
├── 📤 CAMPOS: visitante, propiedad, fechas_programadas, ingreso/salida_real
└── 🎯 FUNCIÓN: Control de acceso de visitantes

🚨 EVENTOS DE SEGURIDAD:
GET/POST/PUT/DELETE /eventos/
├── 📥 FILTROS: tipo, fecha_hora, ubicacion, gravedad, resuelto
├── 📤 CAMPOS: tipo, descripcion, fecha_hora, ubicacion, gravedad
└── 🎯 FUNCIÓN: Bitácora de incidentes
```

### Control de Acceso (APIs Especializadas):
```
🚗 CONTROL VEHICULAR:
├── POST /control-acceso-vehicular/
│   ├── 📥 RECIBE: {"placa": "ABC123"}
│   ├── 📤 DEVUELVE: {"detail": "Acceso permitido", "tipo": "residente"}
│   └── 🎯 FUNCIÓN: Validar acceso por placa

├── POST /control-salida-vehicular/
│   ├── 📥 RECIBE: {"placa": "ABC123"}
│   └── 🎯 FUNCIÓN: Registrar salida vehicular

🤖 INTELIGENCIA ARTIFICIAL:
├── POST /ia/control-vehicular/
│   ├── 📥 RECIBE: Imagen del vehículo
│   ├── 🔍 PROCESA: OCR de placa + validación
│   └── 📤 DEVUELVE: Resultado de acceso

├── POST /ia/verificar-rostro/
│   ├── 📥 RECIBE: Imagen facial
│   ├── 🔍 PROCESA: AWS Rekognition
│   └── 📤 DEVUELVE: Identidad verificada
```

### Dashboards y Reportes:
```
📊 DASHBOARDS:
├── GET /dashboard/resumen/ → Estadísticas generales
├── GET /dashboard/series/ → Datos para gráficos
└── GET /dashboard/top-visitantes/ → Visitantes frecuentes

📋 UTILIDADES:
├── GET /visitas-abiertas/ → Visitas sin salida registrada
├── POST /cerrar-visitas-vencidas/ → Cerrar visitas automáticamente
├── GET /export/visitas.csv → Exportar a CSV
└── GET /detecciones/ → Historial de detecciones IA
```

### Sistema de Permisos por Rol:
```
🔐 CONTROL DE ACCESO:
├── PROPIETARIO → Ve todo, puede gestionar todo
├── SEGURIDAD → Ve todo, gestiona eventos y accesos
├── RESIDENTE → Solo sus propias visitas y vehículos
└── GENERAL → Solo lectura de información básica
```

---

## 🔧 MÓDULO MANTENIMIENTO

### Base: /api/mantenimiento/

```
👨‍🔧 PERSONAL:
GET/POST/PUT/DELETE /personal/
├── 📥 FILTROS: activo, especialidad, nombre
├── 📤 CAMPOS: nombre, telefono, especialidad, activo
├── 🎯 ESPECIALIDADES:
│   ├── ELECTRICIDAD, PLOMERIA, JARDINERIA
│   ├── PINTURA, LIMPIEZA, CARPINTERIA
│   └── AIRES, GENERAL
└── 🎯 FUNCIÓN: Gestión de personal técnico

📝 SOLICITUDES:
GET/POST/PUT/DELETE /solicitudes/
├── 📥 FILTROS: estado, propiedad, asignado_a, fechas, prioridad
├── 📤 CAMPOS: titulo, descripcion, propiedad, estado, prioridad
├── 🔧 ACCIONES ESPECIALES:
│   ├── POST /solicitudes/{id}/cambiar_estado/
│   │   ├── 📥 RECIBE: {"estado": "EN_PROGRESO"}
│   │   └── 🎯 FUNCIÓN: Cambiar estado de solicitud
│   └── POST /solicitudes/{id}/asignar/
│       ├── 📥 RECIBE: {"personal_id": 1}
│       └── 🎯 FUNCIÓN: Asignar técnico a solicitud
└── 🎯 FUNCIÓN: Gestión de mantenimientos
```

### Estados de Solicitudes:
```
📋 FLUJO DE ESTADOS:
PENDIENTE → EN_PROGRESO → COMPLETADA → CERRADA
     ↓         ↓            ↓          ↓
   🔵 Nueva   🟡 Trabajando  🟢 Lista   ⚫ Finalizada
```

### Sistema de Permisos:
```
🔐 CONTROL DE ACCESO:
├── PROPIETARIO → Gestiona personal y todas las solicitudes
├── MANTENIMIENTO → Actualiza solicitudes asignadas
├── RESIDENTE → Crea solicitudes, ve las propias
└── OTROS → Solo lectura
```

### Validaciones de Negocio:
```
⚠️ REGLAS DE NEGOCIO:
├── Residentes morosos no pueden crear solicitudes
├── Solo personal activo puede ser asignado
├── Especialidad debe coincidir con tipo de trabajo
└── Cambios de estado deben seguir flujo lógico
```

---

## 📱 MÓDULO NOTIFICACIONES

### Base: /api/notificaciones/

```
📱 GESTIÓN DE DISPOSITIVOS:
├── POST /token/
│   ├── 📥 RECIBE: {"token": "fcm_device_token", "platform": "android"}
│   ├── 📤 DEVUELVE: Token registrado
│   └── 🎯 FUNCIÓN: Registrar dispositivo para push notifications

├── POST /registrar-dispositivo/
│   ├── 📥 RECIBE: {"token_dispositivo": "...", "plataforma": "ios"}
│   └── 🎯 FUNCIÓN: Registro alternativo de dispositivo

📢 ENVÍO DE NOTIFICACIONES:
└── POST /demo/ (Solo Admin)
    ├── 📥 RECIBE: {"title": "...", "body": "...", "user_id": 1}
    ├── 🔍 PROCESA: Envío via Firebase FCM
    └── 📤 DEVUELVE: Resultado del envío
```

### Integración con Firebase:
```
🔥 FIREBASE FCM:
├── 🔧 CONFIGURACIÓN: settings.py → Firebase credentials
├── 📱 PLATAFORMAS: Android, iOS, Web
├── 🎯 TARGETING: Por usuario específico o broadcast
└── 📊 MÉTRICAS: Tokens activos, envíos exitosos
```

---

## 🔄 FLUJOS DE INTEGRACIÓN

### Flujo de Registro y Autenticación:
```
1. 👤 REGISTRO INICIAL:
   POST /api/registro/ → Usuario creado → Token generado

2. 🔐 LOGIN POSTERIOR:
   POST /api/login/ → Token DRF → Sesión activa

3. 📱 REGISTRO DISPOSITIVO:
   POST /api/dispositivos/registrar/ → Push notifications habilitadas

4. 🎭 REGISTRO FACIAL (Opcional):
   POST /api/usuarios/reconocimiento/registrar-rostro/ → AWS Rekognition
```

### Flujo de Control de Acceso:
```
1. 🚗 LLEGADA VEHÍCULO:
   Cámara → IA → OCR placa → POST /api/seguridad/ia/control-vehicular/

2. ✅ VALIDACIÓN:
   Sistema → Busca vehículo → Valida permisos → Respuesta acceso

3. 📝 REGISTRO:
   Acceso concedido → Actualiza visita → Notifica residente

4. 🚪 SALIDA:
   POST /api/seguridad/control-salida-vehicular/ → Cierra visita
```

### Flujo de Gestión Financiera:
```
1. 📋 GENERACIÓN GASTOS:
   POST /api/finanzas/expensas/generar/ → Gastos mensuales automáticos

2. 💰 PROCESO DE PAGO:
   Residente → Selecciona gastos → POST /api/finanzas/gastos/pagar_en_lote/

3. 🧾 COMPROBANTE:
   GET /api/finanzas/pagos/{id}/comprobante/ → PDF descargable

4. 📊 REPORTES:
   Admin → GET /api/finanzas/reportes/resumen/ → Estado financiero
```

### Flujo de Mantenimiento:
```
1. 📝 SOLICITUD:
   Residente → POST /api/mantenimiento/solicitudes/ → Ticket creado

2. 👨‍🔧 ASIGNACIÓN:
   Admin → POST /api/mantenimiento/solicitudes/{id}/asignar/ → Técnico asignado

3. 🔧 TRABAJO:
   Técnico → POST /api/mantenimiento/solicitudes/{id}/cambiar_estado/ → "EN_PROGRESO"

4. ✅ FINALIZACIÓN:
   Técnico → Cambia estado → "COMPLETADA" → Notifica residente
```

---

## 📊 DIAGRAMA DE ARQUITECTURA

```
🌐 FRONTEND APPLICATIONS
├── 📱 Mobile App (React Native/Flutter)
├── 💻 Web Admin Panel (React/Vue)
└── 🎮 Security Terminal (Kiosk Mode)
                    ↓
🔗 API GATEWAY (/api/)
├── 🔐 Authentication Layer (DRF Token)
├── 🛡️ Permissions System (Role-based)
└── 📝 Request/Response Processing
                    ↓
🏗️ DJANGO BACKEND SERVICES
├── 👥 usuarios/ → User management + profiles + auth
├── 🏠 condominio/ → Properties + common areas + rules
├── 💰 finanzas/ → Expenses + payments + reservations
├── 🛡️ seguridad/ → Access control + visitors + vehicles
├── 🔧 mantenimiento/ → Maintenance requests + staff
├── 📱 notificaciones/ → Push notifications + devices
└── 📊 auditoria/ → System logs + audit trail
                    ↓
🗄️ DATA LAYER
├── 🐘 PostgreSQL → Main database (production)
├── 🗃️ SQLite → Development database
├── 📁 AWS S3 → File storage (images, PDFs)
├── 🤖 AWS Rekognition → Facial recognition
└── 🔥 Firebase FCM → Push notifications
                    ↓
🔌 EXTERNAL INTEGRATIONS
├── 💳 PagosNet API → Payment gateway
├── 📧 Email Service → Notifications
├── 📱 SMS Service → Alerts
└── 🤖 AI Services → Computer vision
```

### Flujo de Datos Completo:
```
📱 CLIENTE → 🔗 API → 🏗️ BACKEND → 🗄️ DATABASE
    ↑                                     ↓
📢 RESPUESTA ← 🔍 PROCESAMIENTO ← 📊 DATOS
```

### Sistema de Filtros Avanzados:
```
🔍 DJANGO-FILTER BACKENDS:
├── DjangoFilterBackend → ?field=value&field__gte=100
├── SearchFilter → ?search=texto
├── OrderingFilter → ?ordering=-fecha
└── Paginación → ?page=2&page_size=20

📋 DISPONIBLE EN TODOS LOS VIEWSETS:
├── Filtros por campo exacto: field=value
├── Filtros de rango: field__gte, field__lte
├── Filtros de texto: field__icontains
├── Filtros booleanos: field=true/false
└── Filtros de nulos: field__isnull=true
```

---

## 🎯 RESUMEN DE ENDPOINTS PRINCIPALES

```
🔐 AUTENTICACIÓN:
POST /api/login/ → Token de acceso
POST /api/registro/ → Registro de usuario

👥 USUARIOS:
CRUD /api/usuarios/residentes/ → Gestión residentes
GET /api/usuarios/perfil/ → Perfil personal

🏠 CONDOMINIO:
CRUD /api/condominio/propiedades/ → Unidades
GET /api/condominio/areas-comunes/ → Espacios comunes
CRUD /api/condominio/avisos/ → Comunicados

💰 FINANZAS:
CRUD /api/finanzas/gastos/ → Expensas
CRUD /api/finanzas/pagos/ → Pagos
CRUD /api/finanzas/reservas/ → Reservas
GET /api/finanzas/reportes/* → Reportes financieros

🛡️ SEGURIDAD:
CRUD /api/seguridad/visitas/ → Control visitantes
CRUD /api/seguridad/vehiculos/ → Control vehicular
POST /api/seguridad/control-acceso-vehicular/ → Acceso
POST /api/seguridad/ia/* → Servicios IA

🔧 MANTENIMIENTO:
CRUD /api/mantenimiento/solicitudes/ → Tickets
CRUD /api/mantenimiento/personal/ → Personal técnico

📱 NOTIFICACIONES:
POST /api/notificaciones/token/ → Registrar dispositivo
POST /api/notificaciones/demo/ → Enviar notificación
```

---

## 🔒 SISTEMA DE SEGURIDAD

### Niveles de Acceso:
```
🏢 PROPIETARIO (Admin Total):
├── ✅ Todos los endpoints CRUD
├── ✅ Reportes y dashboards
├── ✅ Gestión de usuarios
└── ✅ Configuración del sistema

🏡 RESIDENTE (Usuario Normal):
├── ✅ Sus propios datos y transacciones
├── ✅ Crear solicitudes de mantenimiento
├── ✅ Gestionar sus visitas y vehículos
└── ❌ No ve datos de otros residentes

🛡️ SEGURIDAD (Personal):
├── ✅ Control de acceso completo
├── ✅ Gestión de visitantes y vehículos
├── ✅ Eventos de seguridad
└── ❌ No accede a finanzas

🔧 MANTENIMIENTO (Personal):
├── ✅ Solicitudes asignadas
├── ✅ Actualizar estado de trabajos
├── ✅ Ver personal y especialidades
└── ❌ No accede a otros módulos
```

### Validaciones de Negocio:
```
⚠️ REGLAS IMPLEMENTADAS:
├── Residentes morosos no pueden crear solicitudes
├── Solo propietarios pueden modificar datos críticos
├── Personal inactivo no puede ser asignado
├── Fechas de reservas deben ser futuras
├── Pagos no pueden exceder deuda pendiente
└── Estados deben seguir flujos lógicos
```

---

Este sistema está completamente funcional con filtros avanzados, control de permisos por roles, integración con servicios externos (AWS, Firebase, PagosNet) y un flujo completo desde la gestión de usuarios hasta el control de acceso con IA. 🚀