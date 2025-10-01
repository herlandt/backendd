# API Test Endpoints - Guía de Pruebas del Backend

## URLs Principales para Pruebas

### 📋 **Documentación Automática (SIN AUTENTICACIÓN)**
- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **ReDoc**: http://localhost:8000/api/schema/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### 🔐 **Autenticación**
- **Login**: `POST http://localhost:8000/api/login/`
- **Registro**: `POST http://localhost:8000/api/registro/`

### 🏠 **Endpoints Principales (CON AUTENTICACIÓN)**

#### Usuarios
- `GET http://localhost:8000/api/usuarios/`
- `POST http://localhost:8000/api/usuarios/`

#### Seguridad
- `GET http://localhost:8000/api/seguridad/visitas/`
- `POST http://localhost:8000/api/seguridad/visitas/`
- `GET http://localhost:8000/api/seguridad/control-acceso/`

#### Condominio
- `GET http://localhost:8000/api/condominio/propiedades/`
- `GET http://localhost:8000/api/condominio/avisos/`

#### Finanzas
- `GET http://localhost:8000/api/finanzas/gastos/`
- `GET http://localhost:8000/api/finanzas/pagos/`
- `GET http://localhost:8000/api/finanzas/estado-cuenta/`

#### Mantenimiento
- `GET http://localhost:8000/api/mantenimiento/solicitudes/`

---

## 🧪 **Cómo Probar el Backend**

### 1. **Sin Autenticación (Público)**
```powershell
# Swagger UI
Invoke-WebRequest -Uri "http://localhost:8000/api/schema/swagger-ui/" -Method GET

# Schema JSON
Invoke-WebRequest -Uri "http://localhost:8000/api/schema/" -Method GET
```

### 2. **Registro de Usuario**
```powershell
$body = @{
    username = "testuser"
    password = "testpass123"
    email = "test@example.com"
    first_name = "Test"
    last_name = "User"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/registro/" -Method POST -Body $body -ContentType "application/json"
```

### 3. **Login para Obtener Token**
```powershell
$loginBody = @{
    username = "testuser"
    password = "testpass123"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/api/login/" -Method POST -Body $loginBody -ContentType "application/json"
$token = ($response.Content | ConvertFrom-Json).token
```

### 4. **Usar Endpoints con Autenticación**
```powershell
# Ejemplo: Obtener visitas
$headers = @{
    "Authorization" = "Token $token"
    "Content-Type" = "application/json"
}

Invoke-WebRequest -Uri "http://localhost:8000/api/seguridad/visitas/" -Method GET -Headers $headers
```

---

## 🔧 **Endpoints de Prueba Simples**

### Admin (Ya funciona)
- **Django Admin**: http://localhost:8000/admin/

### API Testing Tools
1. **Postman**: Importar colección desde Swagger
2. **Insomnia**: Usar OpenAPI schema
3. **curl/PowerShell**: Comandos manuales

---

## 📊 **Estado de Endpoints**

| Endpoint | Estado | Autenticación |
|----------|--------|---------------|
| `/admin/` | ✅ Funciona | Django Admin |
| `/api/schema/swagger-ui/` | ✅ Funciona | No requerida |
| `/api/login/` | ✅ Funciona | No requerida |
| `/api/registro/` | ✅ Funciona | No requerida |
| `/api/seguridad/visitas/` | ✅ Funciona | Token requerido |
| `/api/` | ✅ Vista de Bienvenida | - |

---

## 💡 **Próximos Pasos**

1. **Crear vista de bienvenida en `/api/`**
2. **Configurar CORS para frontend**
3. **Agregar endpoints de salud**
4. **Configurar throttling**

---

**Nota**: La mayoría de endpoints requieren autenticación con Token. Usa la documentación Swagger para pruebas interactivas.