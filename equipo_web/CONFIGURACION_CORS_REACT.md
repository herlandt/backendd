# 🌐 CONFIGURACIÓN CORS PARA EQUIPO WEB - REACT

## ✅ **CORS CONFIGURADO CORRECTAMENTE EN BACKEND DJANGO**

**Fecha:** Octubre 2, 2025  
**Para:** Equipo de Desarrollo Web (React)  
**Backend:** Django REST API  

---

## 🎯 **CONFIGURACIÓN ACTUAL**

### **✅ CORS Headers Instalado y Configurado**
```python
# En config/settings.py

# CORS permitido para todos los puertos comunes de React
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",      # Create React App (puerto por defecto)
    "http://localhost:5173",      # Vite React (puerto por defecto)
    "http://127.0.0.1:5173",      # Alternativa localhost Vite
    "http://127.0.0.1:3000",      # Alternativa localhost CRA
    "http://localhost:3001",      # Puerto alternativo React
    "http://localhost:5174",      # Puerto alternativo Vite
    "http://127.0.0.1:3001",      # Alternativa localhost
    "http://127.0.0.1:5174",      # Alternativa localhost
]

# Para desarrollo: permitir TODOS los orígenes de localhost
CORS_ALLOW_ALL_ORIGINS = DEBUG  # True en desarrollo

# Headers adicionales permitidos
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',          # ← IMPORTANTE para JWT/Token
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-api-key',             # ← Para APIs con clave de seguridad
]

# Métodos HTTP permitidos
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Permitir cookies y credenciales
CORS_ALLOW_CREDENTIALS = True
```

---

## 🔗 **ENDPOINTS DISPONIBLES PARA REACT**

### **🌐 URL Base del Backend:**
```
http://127.0.0.1:8000/api/
```

### **🔐 Autenticación:**
```javascript
// Headers requeridos para autenticación
const headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Token <tu_token_aqui>',  // ← Importante
}

// Endpoint de login
POST /api/login/
Body: { "username": "admin", "password": "admin123" }
Response: { "token": "abc123...", "user": {...} }
```

### **👥 Usuarios de Prueba Disponibles:**
```javascript
// Usuarios sincronizados y verificados
const testUsers = {
  admin: 'admin123',           // Administrador completo
  residente1: 'isaelOrtiz2',   // Residente principal (RECOMENDADO)
  propietario1: 'joseGarcia3', // Propietario
  inquilino1: 'anaLopez4',     // Inquilino
  seguridad1: 'guardia123',    // Personal de seguridad
  mantenimiento1: 'mant456',   // Personal de mantenimiento
  invitado1: 'invCarlos5'      // Invitado
}
```

---

## 📡 **ENDPOINTS API PRINCIPALES**

### **🔐 Autenticación:**
```
POST /api/login/                     # Login de usuario
POST /api/logout/                    # Logout de usuario
GET  /api/usuarios/perfil/           # Perfil del usuario actual
```

### **💰 Finanzas:**
```
GET  /api/finanzas/gastos/                    # Lista de gastos
POST /api/finanzas/gastos/{id}/registrar_pago/ # Registrar pago
GET  /api/finanzas/estado-cuenta/             # Estado de cuenta
GET  /api/finanzas/comprobantes/              # Comprobantes
```

### **🏠 Condominio:**
```
GET  /api/condominio/avisos/          # Avisos del condominio
GET  /api/condominio/propiedades/     # Propiedades
GET  /api/condominio/areas-comunes/   # Áreas comunes
```

### **🛡️ Seguridad:**
```
GET  /api/seguridad/visitas/          # Gestión de visitas
GET  /api/seguridad/visitantes/       # Visitantes
GET  /api/seguridad/vehiculos/        # Vehículos registrados
GET  /api/seguridad/eventos/          # Eventos de seguridad
```

### **🔧 Mantenimiento:**
```
GET  /api/mantenimiento/solicitudes/  # Solicitudes de mantenimiento
POST /api/mantenimiento/solicitudes/  # Crear solicitud
GET  /api/mantenimiento/tipos/        # Tipos de mantenimiento
```

### **📢 Notificaciones:**
```
GET  /api/notificaciones/             # Notificaciones del usuario
POST /api/notificaciones/marcar-leida/{id}/ # Marcar como leída
```

---

## 🧪 **TESTING DE CONECTIVIDAD**

### **✅ Test Básico de Conectividad:**
```javascript
// Test 1: Verificar que el backend responde
fetch('http://127.0.0.1:8000/api/')
  .then(response => response.json())
  .then(data => console.log('✅ Backend conectado:', data))
  .catch(error => console.log('❌ Error:', error));

// Test 2: Login con usuario de prueba
fetch('http://127.0.0.1:8000/api/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'residente1',
    password: 'isaelOrtiz2'
  })
})
.then(response => response.json())
.then(data => {
  if (data.token) {
    console.log('✅ Login exitoso, token:', data.token);
    localStorage.setItem('token', data.token);
  }
})
.catch(error => console.log('❌ Error login:', error));

// Test 3: Usar token para obtener perfil
const token = localStorage.getItem('token');
fetch('http://127.0.0.1:8000/api/usuarios/perfil/', {
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log('✅ Perfil obtenido:', data))
.catch(error => console.log('❌ Error perfil:', error));
```

---

## ⚙️ **CONFIGURACIÓN EN REACT**

### **📦 Configuración de Axios (Recomendado):**
```javascript
// src/api/config.js
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token automáticamente
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Interceptor para manejar errores de autenticación
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### **🔐 Servicio de Autenticación:**
```javascript
// src/services/authService.js
import apiClient from '../api/config';

export const authService = {
  // Login de usuario
  async login(username, password) {
    const response = await apiClient.post('/login/', {
      username,
      password
    });
    
    if (response.data.token) {
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    
    return response.data;
  },

  // Logout de usuario
  async logout() {
    try {
      await apiClient.post('/logout/');
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  },

  // Obtener perfil actual
  async getProfile() {
    const response = await apiClient.get('/usuarios/perfil/');
    return response.data;
  },

  // Verificar si usuario está autenticado
  isAuthenticated() {
    return !!localStorage.getItem('token');
  },

  // Obtener token
  getToken() {
    return localStorage.getItem('token');
  },

  // Obtener usuario actual
  getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }
};
```

### **💰 Servicio de Finanzas:**
```javascript
// src/services/finanzasService.js
import apiClient from '../api/config';

export const finanzasService = {
  // Obtener gastos del usuario
  async getGastos() {
    const response = await apiClient.get('/finanzas/gastos/');
    return response.data;
  },

  // Registrar pago
  async registrarPago(gastoId, datosPago) {
    const response = await apiClient.post(
      `/finanzas/gastos/${gastoId}/registrar_pago/`,
      datosPago
    );
    return response.data;
  },

  // Obtener estado de cuenta
  async getEstadoCuenta() {
    const response = await apiClient.get('/finanzas/estado-cuenta/');
    return response.data;
  }
};
```

---

## 🚨 **SOLUCIÓN DE PROBLEMAS COMUNES**

### **❌ Error: "Login exitoso pero no redirige"**
**Síntoma:** Login funciona, token se obtiene, pero no navega al dashboard  
**Solución:** 
1. Verificar que `useAuth` actualice `isAuthenticated = true`
2. Verificar que `LoginPage` ejecute `navigate('/dashboard')`
3. Usar `equipo_web/debug_login_flow.html` para diagnosticar

```typescript
// Solución en LoginPage.tsx
const handleLogin = async (e: React.FormEvent) => {
  const result = await login(formData.username, formData.password);
  
  if (result.success) {
    console.log('✅ Login exitoso, navegando...');
    navigate('/dashboard'); // ← DEBE EJECUTARSE
  }
};
```

### **❌ Error: "CORS policy blocked"**
**Solución:** El backend ya está configurado correctamente. Asegúrate de que:
1. El servidor Django esté corriendo en `http://127.0.0.1:8000`
2. Tu React esté en uno de los puertos configurados (3000, 5173, etc.)

### **❌ Error: "401 Unauthorized"**
**Solución:** 
1. Verifica que estés enviando el header `Authorization: Token <token>`
2. Usa uno de los usuarios de prueba verificados
3. El token debe obtenerse del endpoint `/api/login/`

### **❌ Error: "404 Not Found"**
**Solución:**
1. Verifica que el endpoint existe en la documentación: `http://127.0.0.1:8000/api/schema/swagger-ui/`
2. Asegúrate de usar la URL base correcta: `http://127.0.0.1:8000/api/`

### **❌ Error: "500 Internal Server Error"**
**Solución:**
1. Revisa los logs del servidor Django
2. Verifica que todos los campos requeridos estén en el body de la petición
3. Verifica que el formato de datos sea correcto (JSON)

---

## 📚 **DOCUMENTACIÓN ADICIONAL**

### **🔍 Explorar API:**
```
http://127.0.0.1:8000/api/schema/swagger-ui/
```

### **📄 Schema OpenAPI:**
```
http://127.0.0.1:8000/api/schema/
```

### **🔧 Panel de Administración Django:**
```
http://127.0.0.1:8000/admin/
Usuario: admin
Contraseña: admin123
```

---

## ✅ **VERIFICACIÓN FINAL**

### **Checklist para el Equipo React:**
- [ ] Backend Django corriendo en `http://127.0.0.1:8000`
- [ ] React app corriendo en puerto configurado (3000, 5173, etc.)
- [ ] Test de conectividad básica funcionando
- [ ] Login con `residente1` / `isaelOrtiz2` exitoso
- [ ] Token obtenido y guardado correctamente
- [ ] Requests autenticados funcionando
- [ ] Endpoints principales respondiendo

### **✅ Herramientas de Debugging:**
1. **`equipo_web/debug_login_flow.html`** - Diagnóstico completo de login
2. **`equipo_web/test_cors_react.html`** - Test de conectividad CORS  
3. **`equipo_web/SOLUCION_REDIRECCION_LOGIN.md`** - Guía de solución detallada

### **🎯 Usuario Recomendado para Pruebas:**
```
Username: residente1
Password: isaelOrtiz2
Rol: Residente con acceso completo a funcionalidades básicas
```

---

## 🚀 **¡LISTO PARA DESARROLLO!**

El backend Django está completamente configurado para trabajar con React. Todas las configuraciones de CORS, autenticación y endpoints están operativas.

**🎉 El equipo web puede comenzar el desarrollo inmediatamente usando esta configuración.** 

Para cualquier problema o duda adicional, consultar la documentación de la API en Swagger UI o contactar al equipo backend.

---

**📞 Soporte Backend Disponible 24/7** ✅