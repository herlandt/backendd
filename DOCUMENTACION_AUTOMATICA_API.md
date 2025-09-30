# 📚 DOCUMENTACIÓN AUTOMÁTICA DE LA API - Sistema de Condominio

## 🎯 ¿Por qué usar la documentación automática?

En lugar de crear un informe manual extenso, el sistema utiliza **drf-spectacular** que genera automáticamente documentación completa, interactiva y siempre actualizada de todos los endpoints de la API.

## 🌐 URLs de Documentación Disponibles

### 🔗 Swagger UI (Interactiva)
```
http://localhost:8000/api/schema/swagger-ui/
```
- **Interfaz visual moderna**
- **Prueba endpoints en tiempo real**
- **Documentación interactiva**
- **Ejemplos de request/response**
- **Esquemas de datos detallados**

### 📖 ReDoc (Documentación Estática)
```
http://localhost:8000/api/schema/redoc/
```
- **Documentación limpia y ordenada**
- **Fácil navegación**
- **Ideal para lectura**
- **Exportable y compartible**

### 🔧 Esquema OpenAPI (JSON)
```
http://localhost:8000/api/schema/
```
- **Esquema completo en formato OpenAPI 3.0**
- **Importable en herramientas como Postman**
- **Generación automática de SDKs**
- **Integración con herramientas de testing**

## 🚀 Ventajas de la Documentación Automática

### ✅ **Siempre Actualizada**
- Se genera automáticamente del código
- No hay riesgo de documentación desactualizada
- Refleja cambios en tiempo real

### ✅ **Completamente Detallada**
- **Cada endpoint documentado** con métodos HTTP
- **Parámetros de entrada** con tipos y validaciones
- **Respuestas esperadas** con códigos de estado
- **Esquemas de datos** con todos los campos
- **Ejemplos reales** de uso

### ✅ **Interactiva**
- **Prueba endpoints** directamente desde la documentación
- **Autenticación integrada** para pruebas con token
- **Respuestas en tiempo real**
- **Debugging integrado**

### ✅ **Profesional**
- **Estándar OpenAPI 3.0** reconocido internacionalmente
- **Compatible** con herramientas de desarrollo
- **Exportable** a múltiples formatos
- **Compartible** con equipos de desarrollo

## 📋 ¿Qué Encontrarás en la Documentación?

### 🔐 **Módulo de Autenticación**
```
POST /api/login/
├── 📥 Entrada: username, password
├── 📤 Salida: token de autenticación
├── 🔍 Códigos: 200 (éxito), 400 (error)
└── 📝 Descripción: Proceso completo de autenticación

POST /api/registro/
├── 📥 Entrada: usuario, email, contraseña
├── 📤 Salida: usuario creado + token
├── 🔍 Validaciones: formato email, longitud contraseña
└── 📝 Proceso: Creación automática de perfil
```

### 👥 **Módulo de Usuarios**
```
CRUD /api/usuarios/residentes/
├── 📊 Filtros: propiedad, usuario, email, nombre
├── 🔍 Búsqueda: por nombre, email, propiedad
├── 📈 Ordenamiento: por fecha, usuario, propiedad
├── 🔐 Permisos: Solo administradores
└── 📋 Campos: usuario, propiedad, rol, fcm_token

GET /api/usuarios/perfil/
├── 📤 Salida: Perfil del usuario autenticado
├── 📊 Incluye: datos usuario, propiedad, rol
└── 🔐 Permisos: Usuario autenticado
```

### 🏠 **Módulo de Condominio**
```
CRUD /api/condominio/propiedades/
├── 📊 Filtros: numero_casa, metros_cuadrados, propietario
├── 🔍 Búsqueda: por número de casa
├── 📋 Campos: numero_casa, propietario, metros_cuadrados
└── 🎯 Función: Gestión de unidades habitacionales

GET /api/condominio/areas-comunes/
├── 📊 Filtros: nombre, capacidad, costo_reserva
├── 📋 Campos: nombre, descripción, capacidad, horarios
└── 🎯 Función: Espacios compartidos del condominio
```

### 💰 **Módulo Financiero (Completo)**
```
CRUD /api/finanzas/gastos/
├── 📊 Filtros: mes, año, pagado, monto, fecha_vencimiento
├── 🔧 Acciones Especiales:
│   ├── POST .../registrar_pago/ → Pagar gasto individual
│   ├── POST .../pagar_en_lote/ → Pagar múltiples gastos
│   └── POST .../crear_mensual/ → Crear gastos recurrentes
├── 🔐 Permisos: Propietarios (escritura), Residentes (lectura)
└── 📋 Proceso Completo: Desde creación hasta pago confirmado

POST /api/finanzas/pagos/{id}/simular/
├── 📥 Entrada: ID del pago
├── 🔄 Proceso: Simulación de pasarela de pagos
├── 📤 Salida: Confirmación + estado actualizado
└── 🎯 Función: Demo de integración con PagosNet
```

### 🛡️ **Módulo de Seguridad (IA Integrada)**
```
POST /api/seguridad/control-acceso-vehicular/
├── 📥 Entrada: {"placa": "ABC123"}
├── 🔄 Proceso: Validación en BD + verificación de visitas
├── 📤 Salida: Acceso permitido/denegado + tipo (residente/visitante)
└── 🎯 Función: Control automático de acceso vehicular

POST /api/seguridad/ia/control-vehicular/
├── 📥 Entrada: Imagen del vehículo
├── 🤖 Proceso: OCR de placa + validación automática
├── 📤 Salida: Resultado de acceso + eventos registrados
└── 🔐 Permisos: API Key requerida (cámaras de seguridad)

POST /api/seguridad/ia/verificar-rostro/
├── 📥 Entrada: Imagen facial
├── 🤖 Proceso: AWS Rekognition + matching en BD
├── 📤 Salida: Identidad verificada + porcentaje de confianza
└── 🎯 Función: Control de acceso biométrico
```

### 🔧 **Módulo de Mantenimiento**
```
CRUD /api/mantenimiento/solicitudes/
├── 📊 Filtros: estado, prioridad, asignado_a, fecha
├── 🔧 Acciones Especiales:
│   ├── POST .../cambiar_estado/ → Actualizar estado de solicitud
│   └── POST .../asignar/ → Asignar técnico especializado
├── 📋 Estados: PENDIENTE → EN_PROGRESO → COMPLETADA → CERRADA
└── 🔐 Permisos: Residentes (crear), Personal (actualizar), Propietarios (gestionar)
```

## 🔥 Funcionalidades Avanzadas Documentadas

### 🔍 **Sistema de Filtros (Todos los Endpoints)**
```
Filtros por Campo:
├── ?campo=valor → Coincidencia exacta
├── ?campo__gte=100 → Mayor o igual que
├── ?campo__lte=500 → Menor o igual que
└── ?campo__icontains=texto → Contiene texto

Búsqueda Global:
├── ?search=termino → Busca en múltiples campos
└── Ejemplo: ?search=juan garcia

Ordenamiento:
├── ?ordering=campo → Ascendente
├── ?ordering=-campo → Descendente
└── ?ordering=campo1,-campo2 → Múltiple

Paginación:
├── ?page=2 → Página específica
└── ?page_size=20 → Elementos por página
```

### 📊 **Reportes y Dashboards**
```
GET /api/finanzas/reportes/estado-morosidad/
├── 📤 Salida: Lista completa de residentes morosos
├── 📊 Incluye: Deuda total, gastos pendientes, contacto
└── 🎯 Uso: Gestión de cobranzas

GET /api/seguridad/dashboard/resumen/
├── 📤 Salida: Estadísticas en tiempo real
├── 📊 Incluye: Visitas abiertas, ingresos del día
└── 🎯 Uso: Monitor de seguridad
```

## 🛠️ Cómo Usar la Documentación

### 1. **Navegación**
- **Por módulos**: Usuarios, Condominio, Finanzas, etc.
- **Por endpoints**: GET, POST, PUT, DELETE
- **Por funcionalidad**: CRUD, Reportes, Acciones especiales

### 2. **Pruebas en Vivo**
```
1. Hacer clic en cualquier endpoint
2. Ver parámetros requeridos y opcionales
3. Completar formulario con datos de prueba
4. Ejecutar directamente desde la interfaz
5. Ver respuesta en tiempo real
```

### 3. **Autenticación**
```
1. Ir a POST /api/login/
2. Introducir username y password
3. Copiar el token de la respuesta
4. Hacer clic en "Authorize" (🔒)
5. Pegar: Token tu_token_aqui
6. Ahora puedes probar endpoints protegidos
```

### 4. **Ejemplos de Uso**
Cada endpoint incluye:
- **Ejemplo de request** con datos reales
- **Ejemplo de response** con estructura completa
- **Códigos de error** con explicaciones
- **Validaciones** de campos requeridos

## 🎯 Casos de Uso Específicos

### 👨‍💻 **Para Desarrolladores Frontend**
- **Especificaciones exactas** de cada endpoint
- **Tipos de datos** para TypeScript/JavaScript
- **Manejo de errores** documentado
- **Autenticación** paso a paso

### 🏢 **Para Administradores**
- **Flujos completos** de negocio documentados
- **Permisos** y roles claramente definidos
- **Reportes** disponibles y su contenido
- **Configuración** de sistema

### 🔧 **Para Integraciones**
- **Schema OpenAPI** para generar SDKs
- **Webhooks** documentados (PagosNet)
- **APIs de terceros** (AWS, Firebase)
- **Formatos** de request/response

## 🚀 Beneficios vs. Documentación Manual

| Aspecto | Documentación Automática | Manual |
|---------|--------------------------|--------|
| **Actualización** | ✅ Automática siempre | ❌ Manual, puede desactualizarse |
| **Completitud** | ✅ 100% de endpoints | ❌ Puede omitir detalles |
| **Interactividad** | ✅ Pruebas en vivo | ❌ Solo lectura |
| **Mantenimiento** | ✅ Cero esfuerzo | ❌ Requiere tiempo constante |
| **Precisión** | ✅ Generada del código | ❌ Propensa a errores humanos |
| **Estándares** | ✅ OpenAPI 3.0 | ❌ Formato personalizado |
| **Herramientas** | ✅ Compatible con todo | ❌ Limitado |

## 🎉 Conclusión

La documentación automática con **drf-spectacular** proporciona:

✨ **Documentación completa** de todos los 50+ endpoints
✨ **Especificaciones detalladas** de cada función
✨ **Ejemplos prácticos** de uso
✨ **Pruebas interactivas** en tiempo real
✨ **Siempre actualizada** automáticamente
✨ **Estándar profesional** OpenAPI 3.0

**🔗 Accede ahora a:**
- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **ReDoc**: http://localhost:8000/api/schema/redoc/
- **Schema**: http://localhost:8000/api/schema/

Esta documentación automática es **mucho más completa y útil** que cualquier documento manual, ya que proporciona todos los detalles técnicos, ejemplos de uso, y la capacidad de probar la API en tiempo real. 🚀