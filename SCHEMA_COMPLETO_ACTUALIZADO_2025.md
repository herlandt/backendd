# 📋 SCHEMA COMPLETO Y ACTUALIZADO - BACKEND API
## Sistema de Gestión de Condominios

**📅 Generado:** Octubre 2, 2025  
**🔄 Estado:** Completamente actualizado desde servidor en vivo  
**📄 Archivo:** `openapi_schema_actualizado_2025.yaml`  
**📊 Total endpoints:** 100+ endpoints documentados  

---

## 📁 **ARCHIVOS DE SCHEMA DISPONIBLES:**

### **✅ SCHEMA PRINCIPAL (MÁS ACTUALIZADO):**
- **📄 `openapi_schema_actualizado_2025.yaml`** ← **ESTE ES EL ACTUAL**
  - **📅 Generado:** Octubre 2, 2025
  - **📊 Líneas:** 6,206 líneas
  - **✅ Estado:** Completamente actualizado con todos los endpoints
  - **🎯 Versión:** OpenAPI 3.0.3

### **📚 ARCHIVOS ANTERIORES (Referencias):**
- **📄 `openapi_schema_actualizado_2025.yaml`** - ESTE ES EL ACTUAL
- **✅ Archivos anteriores eliminados** - Solo mantenemos el más actualizado

---

## 🎯 **ENDPOINTS PRINCIPALES POR MÓDULO:**

### **🏠 1. API GENERAL**
```yaml
GET  /api/                     # Bienvenida API
GET  /api/schema/              # Schema OpenAPI
GET  /api/schema/swagger-ui/   # Documentación Swagger
GET  /api/schema/redoc/        # Documentación ReDoc
```

### **🔐 2. AUTENTICACIÓN**
```yaml
POST /api/login/               # Iniciar sesión
POST /api/logout/              # Cerrar sesión
GET  /api/usuarios/perfil/     # Perfil del usuario
```

### **👥 3. USUARIOS**
```yaml
GET    /api/usuarios/                    # Lista usuarios
POST   /api/usuarios/                    # Crear usuario
GET    /api/usuarios/{id}/               # Detalle usuario
PUT    /api/usuarios/{id}/               # Actualizar usuario
DELETE /api/usuarios/{id}/               # Eliminar usuario
GET    /api/usuarios/perfil/             # Perfil actual
PUT    /api/usuarios/perfil/             # Actualizar perfil
POST   /api/usuarios/registrar-rostro/   # IA: Registrar rostro
POST   /api/usuarios/crear-admin/        # Crear administrador
```

### **🏢 4. CONDOMINIOS**
```yaml
GET    /api/condominios/        # Lista condominios
POST   /api/condominios/        # Crear condominio
GET    /api/condominios/{id}/   # Detalle condominio
PUT    /api/condominios/{id}/   # Actualizar condominio
DELETE /api/condominios/{id}/   # Eliminar condominio
```

### **🏠 5. PROPIEDADES**
```yaml
GET    /api/propiedades/        # Lista propiedades
POST   /api/propiedades/        # Crear propiedad
GET    /api/propiedades/{id}/   # Detalle propiedad
PUT    /api/propiedades/{id}/   # Actualizar propiedad
DELETE /api/propiedades/{id}/   # Eliminar propiedad
```

### **📢 6. AVISOS**
```yaml
GET    /api/avisos/           # Lista avisos
POST   /api/avisos/           # Crear aviso
GET    /api/avisos/{id}/      # Detalle aviso
PUT    /api/avisos/{id}/      # Actualizar aviso
DELETE /api/avisos/{id}/      # Eliminar aviso
```

### **💰 7. FINANZAS**
```yaml
# GASTOS
GET    /api/gastos/           # Lista gastos
POST   /api/gastos/           # Crear gasto
GET    /api/gastos/{id}/      # Detalle gasto
PUT    /api/gastos/{id}/      # Actualizar gasto
DELETE /api/gastos/{id}/      # Eliminar gasto

# PAGOS
GET    /api/pagos/            # Lista pagos
POST   /api/pagos/            # Crear pago
GET    /api/pagos/{id}/       # Detalle pago
PUT    /api/pagos/{id}/       # Actualizar pago
DELETE /api/pagos/{id}/       # Eliminar pago

# STRIPE (Pagos en línea)
POST   /api/create-payment-intent/     # Crear intención de pago
POST   /api/stripe-webhook/            # Webhook de Stripe
```

### **🛡️ 8. SEGURIDAD**
```yaml
# CONTROL DE ACCESO
GET    /api/controles-acceso/              # Lista controles
POST   /api/controles-acceso/              # Registrar acceso
GET    /api/controles-acceso/{id}/         # Detalle control
PUT    /api/controles-acceso/{id}/         # Actualizar control
DELETE /api/controles-acceso/{id}/         # Eliminar control

# VISITANTES
GET    /api/visitantes/                    # Lista visitantes
POST   /api/visitantes/                    # Registrar visitante
GET    /api/visitantes/{id}/               # Detalle visitante
PUT    /api/visitantes/{id}/               # Actualizar visitante
DELETE /api/visitantes/{id}/               # Eliminar visitante

# VISITAS ABIERTAS (IA)
GET    /api/visitas-abiertas/              # Visitas sin cerrar

# ALERTAS DE SEGURIDAD
GET    /api/alertas-seguridad/             # Lista alertas
POST   /api/alertas-seguridad/             # Crear alerta
GET    /api/alertas-seguridad/{id}/        # Detalle alerta
PUT    /api/alertas-seguridad/{id}/        # Actualizar alerta
DELETE /api/alertas-seguridad/{id}/        # Eliminar alerta
```

### **🔧 9. MANTENIMIENTO**
```yaml
# TICKETS
GET    /api/tickets/          # Lista tickets
POST   /api/tickets/          # Crear ticket
GET    /api/tickets/{id}/     # Detalle ticket
PUT    /api/tickets/{id}/     # Actualizar ticket
DELETE /api/tickets/{id}/     # Eliminar ticket

# ASIGNACIONES
GET    /api/asignaciones/     # Lista asignaciones
POST   /api/asignaciones/     # Crear asignación
GET    /api/asignaciones/{id}/ # Detalle asignación
PUT    /api/asignaciones/{id}/ # Actualizar asignación
DELETE /api/asignaciones/{id}/ # Eliminar asignación
```

### **📊 10. AUDITORÍA**
```yaml
GET    /api/auditoria/bitacora/     # Lista bitácora
GET    /api/auditoria/bitacora/{id}/ # Detalle registro
```

### **📱 11. NOTIFICACIONES**
```yaml
GET    /api/notificaciones/          # Lista notificaciones
POST   /api/notificaciones/          # Crear notificación
GET    /api/notificaciones/{id}/     # Detalle notificación
PUT    /api/notificaciones/{id}/     # Actualizar notificación
DELETE /api/notificaciones/{id}/     # Eliminar notificación

# DISPOSITIVOS FCM
GET    /api/dispositivos-fcm/        # Lista dispositivos
POST   /api/dispositivos-fcm/        # Registrar dispositivo
GET    /api/dispositivos-fcm/{id}/   # Detalle dispositivo
PUT    /api/dispositivos-fcm/{id}/   # Actualizar dispositivo
DELETE /api/dispositivos-fcm/{id}/   # Eliminar dispositivo
```

---

## 🔍 **FILTROS AVANZADOS EN TODOS LOS ENDPOINTS:**

### **🎯 Filtros Disponibles:**
```yaml
# FILTROS DE CAMPO
campo=valor                    # Filtro exacto
campo__icontains=texto        # Contiene texto (insensible a mayúsculas)
campo__gte=valor              # Mayor o igual que
campo__lte=valor              # Menor o igual que
campo__in=valor1,valor2       # En lista de valores

# BÚSQUEDA DE TEXTO
search=término                # Búsqueda en campos de texto

# ORDENAMIENTO
ordering=campo                # Ascendente
ordering=-campo               # Descendente

# EJEMPLOS PRÁCTICOS
/api/usuarios/?search=juan
/api/gastos/?fecha__gte=2025-01-01&fecha__lte=2025-12-31
/api/controles-acceso/?tipo=INGRESO&ordering=-timestamp
/api/pagos/?estado=COMPLETADO&monto__gte=100
```

### **📋 Campos Filtrables por Endpoint:**

#### **👥 Usuarios:**
```yaml
username__icontains, email__icontains, first_name__icontains,
last_name__icontains, is_active, date_joined__gte, date_joined__lte
```

#### **💰 Finanzas:**
```yaml
# Gastos: descripcion__icontains, categoria, monto__gte, monto__lte,
#         fecha__gte, fecha__lte, condominio
# Pagos:  concepto__icontains, monto__gte, monto__lte, estado,
#         fecha_pago__gte, fecha_pago__lte, propiedad, usuario
```

#### **🛡️ Seguridad:**
```yaml
# Control Acceso: tipo, placa__icontains, timestamp__gte, timestamp__lte,
#                 usuario, condominio
# Visitantes:     nombre__icontains, documento__icontains, telefono,
#                 fecha_visita__gte, fecha_visita__lte, propiedad_visitada
```

#### **🔧 Mantenimiento:**
```yaml
# Tickets: titulo__icontains, descripcion__icontains, estado, prioridad,
#          fecha_creacion__gte, fecha_creacion__lte, categoria, asignado_a
```

---

## 🎯 **AUTENTICACIÓN Y PERMISOS:**

### **🔐 Métodos de Autenticación:**
```yaml
# TOKEN AUTHENTICATION (Principal)
Authorization: Token <tu-token-aquí>

# SESSION AUTHENTICATION (Para Swagger UI)
Cookie: sessionid=<session-id>

# Obtener Token
POST /api/login/
{
  "username": "admin",
  "password": "admin123"
}
# Respuesta: {"token": "589db8d96d1dfbd4eeac58d784ad7b3989a0bb21"}
```

### **👤 Roles y Permisos:**
```yaml
PROPIETARIO:    # Acceso completo a todos los endpoints
RESIDENTE:      # Acceso limitado a sus propias finanzas y avisos
SEGURIDAD:      # Acceso a control de acceso y seguridad
MANTENIMIENTO:  # Acceso a tickets de mantenimiento
```

---

## 📊 **MODELOS DE DATOS PRINCIPALES:**

### **👤 Usuario:**
```yaml
User:
  id: integer
  username: string
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  date_joined: datetime

UserProfile:
  user: User
  role: string [PROPIETARIO, RESIDENTE, SEGURIDAD, MANTENIMIENTO]
  especialidad: string (opcional)
  telefono: string
  foto: file
```

### **🏢 Condominio:**
```yaml
Condominio:
  id: integer
  nombre: string
  direccion: string
  telefono: string
  email: string
  administrador: User
  fecha_creacion: datetime
```

### **🏠 Propiedad:**
```yaml
Propiedad:
  id: integer
  numero: string
  tipo: string [APARTAMENTO, CASA, OFICINA, LOCAL]
  condominio: Condominio
  propietario: User
  inquilino: User (opcional)
  area: decimal
  valor_catastral: decimal
```

### **💰 Finanzas:**
```yaml
Gasto:
  id: integer
  descripcion: string
  categoria: string
  monto: decimal
  fecha: date
  condominio: Condominio
  creado_por: User

Pago:
  id: integer
  concepto: string
  monto: decimal
  estado: string [PENDIENTE, COMPLETADO, CANCELADO]
  fecha_pago: datetime
  propiedad: Propiedad
  usuario: User
  stripe_payment_intent_id: string (opcional)
```

### **🛡️ Seguridad:**
```yaml
ControlAcceso:
  id: integer
  tipo: string [INGRESO, SALIDA]
  placa: string (opcional)
  timestamp: datetime
  usuario: User (opcional)
  condominio: Condominio
  observaciones: text

Visitante:
  id: integer
  nombre: string
  documento: string
  telefono: string
  fecha_visita: datetime
  motivo: string
  propiedad_visitada: Propiedad
  autorizado_por: User
  foto: file (opcional)
```

### **🔧 Mantenimiento:**
```yaml
Ticket:
  id: integer
  titulo: string
  descripcion: text
  estado: string [ABIERTO, EN_PROGRESO, RESUELTO, CERRADO]
  prioridad: string [BAJA, MEDIA, ALTA, URGENTE]
  categoria: string
  fecha_creacion: datetime
  fecha_resolucion: datetime (opcional)
  creado_por: User
  asignado_a: User (opcional)
  condominio: Condominio
```

---

## 🚀 **ENDPOINTS DE INTELIGENCIA ARTIFICIAL:**

### **🎯 IA Integrada en el Sistema:**
```yaml
# RECONOCIMIENTO FACIAL
POST /api/usuarios/registrar-rostro/
# Registra rostro en AWS Rekognition

# CONTROL DE ACCESO AUTOMÁTICO
POST /api/controles-acceso/
# Puede usar reconocimiento facial para autorizar acceso

# DETECCIÓN DE VISITANTES
GET /api/visitas-abiertas/
# Lista visitantes que no han registrado salida

# ALERTAS AUTOMÁTICAS
GET /api/alertas-seguridad/
# Alertas generadas por IA (comportamiento sospechoso, etc.)
```

### **🔧 Configuración IA:**
```yaml
# En settings.py
AWS_REKOGNITION_COLLECTION_ID = "condominio_residentes"
SECURITY_API_KEY = "MI_CLAVE_SUPER_SECRETA_12345"

# Headers especiales para IA
X-API-KEY: MI_CLAVE_SUPER_SECRETA_12345  # Para cámaras de IA
```

---

## 📱 **EJEMPLO DE USO COMPLETO:**

### **🔐 1. Autenticación:**
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Respuesta: {"token":"589db8d96d1dfbd4eeac58d784ad7b3989a0bb21"}
```

### **👥 2. Obtener Usuarios:**
```bash
curl -H "Authorization: Token 589db8d96d1dfbd4eeac58d784ad7b3989a0bb21" \
  http://127.0.0.1:8000/api/usuarios/
```

### **🏠 3. Crear Propiedad:**
```bash
curl -X POST http://127.0.0.1:8000/api/propiedades/ \
  -H "Authorization: Token 589db8d96d1dfbd4eeac58d784ad7b3989a0bb21" \
  -H "Content-Type: application/json" \
  -d '{
    "numero": "101",
    "tipo": "APARTAMENTO",
    "condominio": 1,
    "propietario": 2,
    "area": 75.5,
    "valor_catastral": 50000
  }'
```

### **💰 4. Registrar Pago:**
```bash
curl -X POST http://127.0.0.1:8000/api/pagos/ \
  -H "Authorization: Token 589db8d96d1dfbd4eeac58d784ad7b3989a0bb21" \
  -H "Content-Type: application/json" \
  -d '{
    "concepto": "Cuota mensual",
    "monto": 150.00,
    "estado": "COMPLETADO",
    "propiedad": 1,
    "usuario": 2
  }'
```

### **🛡️ 5. Control de Acceso:**
```bash
curl -X POST http://127.0.0.1:8000/api/controles-acceso/ \
  -H "Authorization: Token 589db8d96d1dfbd4eeac58d784ad7b3989a0bb21" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "INGRESO",
    "placa": "ABC123",
    "usuario": 2,
    "condominio": 1,
    "observaciones": "Ingreso autorizado"
  }'
```

---

## 📋 **RESUMEN EJECUTIVO:**

### **✅ Schema Completamente Actualizado:**
- **📄 Archivo:** `openapi_schema_actualizado_2025.yaml`
- **📊 Total líneas:** 6,206 líneas
- **🎯 Endpoints:** 100+ endpoints documentados
- **📅 Fecha:** Octubre 2, 2025
- **✅ Estado:** Generado desde servidor en vivo

### **🎯 Módulos Incluidos:**
- ✅ **Autenticación y Usuarios** (10+ endpoints)
- ✅ **Condominios y Propiedades** (10+ endpoints)
- ✅ **Finanzas Completas** (15+ endpoints)
- ✅ **Seguridad con IA** (20+ endpoints)
- ✅ **Mantenimiento** (10+ endpoints)
- ✅ **Auditoría** (5+ endpoints)
- ✅ **Notificaciones** (10+ endpoints)
- ✅ **Comunicación** (5+ endpoints)

### **🔧 Características Técnicas:**
- ✅ **OpenAPI 3.0.3** estándar
- ✅ **Filtros avanzados** en todos los endpoints
- ✅ **Autenticación por tokens** implementada
- ✅ **Permisos por roles** configurados
- ✅ **Integración IA** documentada
- ✅ **CORS configurado** para frontend web
- ✅ **Documentación Swagger/ReDoc** disponible

**🎉 Este es el schema más completo y actualizado del sistema!**