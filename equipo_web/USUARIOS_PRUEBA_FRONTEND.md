# 👥 USUARIOS DE PRUEBA PARA FRONTEND - Sistema de Condominio

**Fecha:** Octubre 1, 2025  
**Para:** Equipo Frontend  
**Backend:** Django 5.2.6 operativo en `http://127.0.0.1:8000`

---

## 🎯 **USUARIOS CREADOS Y VERIFICADOS**

### **🏢 ADMINISTRADOR / PROPIETARIO**
```json
{
  "username": "admin",
  "password": "admin123",
  "email": "admin@condominio.com",
  "role": "PROPIETARIO",
  "permisos": "Acceso completo a todo el sistema",
  "descripcion": "Usuario administrador con permisos totales"
}
```

### **🏡 RESIDENTE PRINCIPAL**
```json
{
  "username": "residente1",
  "password": "isaelOrtiz2",
  "email": "residente1@gmail.com",
  "role": "RESIDENTE",
  "propiedad": "Apartamento 101",
  "permisos": "Sus propios datos, finanzas, solicitudes, visitas",
  "descripcion": "Residente activo con historial completo"
}
```

### **🏡 RESIDENTE SECUNDARIO**
```json
{
  "username": "residente2",
  "password": "maria2024",
  "email": "maria.garcia@gmail.com",
  "role": "RESIDENTE",
  "propiedad": "Apartamento 201",
  "permisos": "Sus propios datos, finanzas, solicitudes, visitas",
  "descripcion": "Segundo residente para pruebas comparativas"
}
```

### **🛡️ PERSONAL DE SEGURIDAD**
```json
{
  "username": "seguridad1",
  "password": "guardia123",
  "email": "seguridad@condominio.com",
  "role": "SEGURIDAD",
  "permisos": "Control de acceso, visitantes, vehículos, eventos",
  "descripcion": "Personal de seguridad turno diurno"
}
```

### **🔧 PERSONAL DE MANTENIMIENTO ELÉCTRICO**
```json
{
  "username": "electricista1",
  "password": "electrico123",
  "email": "electricista@condominio.com",
  "role": "MANTENIMIENTO",
  "especialidad": "ELECTRICIDAD",
  "permisos": "Solicitudes de mantenimiento eléctrico",
  "descripcion": "Técnico especialista en electricidad"
}
```

### **🔧 PERSONAL DE MANTENIMIENTO PLOMERÍA**
```json
{
  "username": "plomero1",
  "password": "plomeria123",
  "email": "plomero@condominio.com",
  "role": "MANTENIMIENTO",
  "especialidad": "PLOMERIA",
  "permisos": "Solicitudes de mantenimiento de plomería",
  "descripcion": "Técnico especialista en plomería"
}
```

### **🔧 PERSONAL DE MANTENIMIENTO GENERAL**
```json
{
  "username": "mantenimiento1",
  "password": "general123",
  "email": "mantenimiento@condominio.com",
  "role": "MANTENIMIENTO",
  "especialidad": "GENERAL",
  "permisos": "Solicitudes de mantenimiento general",
  "descripcion": "Técnico de mantenimiento general"
}
```

---

## 🧪 **SCRIPTS DE PRUEBA PARA FRONTEND**

### **Test de Autenticación**
```javascript
// Test básico de login
const testUsers = [
  {
    description: "Admin Login",
    username: "admin",
    password: "admin123",
    expectedRole: "PROPIETARIO"
  },
  {
    description: "Residente Login",
    username: "residente1", 
    password: "isaelOrtiz2",
    expectedRole: "RESIDENTE"
  },
  {
    description: "Seguridad Login",
    username: "seguridad1",
    password: "guardia123", 
    expectedRole: "SEGURIDAD"
  },
  {
    description: "Mantenimiento Login",
    username: "electricista1",
    password: "electrico123",
    expectedRole: "MANTENIMIENTO"
  }
];

// Función de prueba
async function testLogin(user) {
  const response = await fetch('http://127.0.0.1:8000/api/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username: user.username,
      password: user.password
    })
  });
  
  if (response.ok) {
    const data = await response.json();
    console.log(`✅ ${user.description}: SUCCESS`, data);
    return data.token;
  } else {
    console.log(`❌ ${user.description}: FAILED`);
    return null;
  }
}
```

### **Test de Endpoints por Rol**
```javascript
// Datos de prueba para cada módulo
const testData = {
  
  // FINANZAS - Para residente1
  finanzas: {
    endpoint: "/api/finanzas/gastos/",
    user: "residente1",
    description: "Ver gastos del residente"
  },
  
  // SEGURIDAD - Para seguridad1  
  seguridad: {
    endpoint: "/api/seguridad/visitas/",
    user: "seguridad1", 
    description: "Gestión de visitas"
  },
  
  // MANTENIMIENTO - Para electricista1
  mantenimiento: {
    endpoint: "/api/mantenimiento/solicitudes/",
    user: "electricista1",
    description: "Solicitudes de mantenimiento"
  },
  
  // CONDOMINIO - Para admin
  condominio: {
    endpoint: "/api/condominio/propiedades/",
    user: "admin",
    description: "Gestión de propiedades"
  }
};
```

---

## 🏠 **DATOS DE PROPIEDADES PARA PRUEBAS**

### **Propiedades Creadas**
```json
[
  {
    "id": 1,
    "numero_casa": "101", 
    "propietario": "residente1",
    "metros_cuadrados": "85.50",
    "descripcion": "Apartamento 2 habitaciones, 2 baños"
  },
  {
    "id": 2,
    "numero_casa": "201",
    "propietario": "residente2", 
    "metros_cuadrados": "92.00",
    "descripcion": "Apartamento 3 habitaciones, 2 baños"
  },
  {
    "id": 3,
    "numero_casa": "301",
    "propietario": "admin",
    "metros_cuadrados": "110.00", 
    "descripcion": "Penthouse 3 habitaciones, 3 baños"
  }
]
```

---

## 💰 **DATOS FINANCIEROS DE PRUEBA**

### **Gastos para residente1**
```json
[
  {
    "concepto": "Administración Octubre 2025",
    "monto": 250000,
    "propiedad": "101",
    "categoria": "administracion",
    "estado": "pendiente",
    "fecha_vencimiento": "2025-10-31"
  },
  {
    "concepto": "Cuota Extraordinaria Pintura",
    "monto": 150000,
    "propiedad": "101", 
    "categoria": "extraordinaria",
    "estado": "pagado",
    "fecha_vencimiento": "2025-09-30"
  }
]
```

### **Multas para residente1**
```json
[
  {
    "concepto": "Ruido después de las 22:00",
    "monto": 50000,
    "propiedad": "101",
    "fecha_multa": "2025-09-25",
    "estado": "pendiente",
    "aplicada_por": "Administración"
  }
]
```

---

## 🛡️ **DATOS DE SEGURIDAD DE PRUEBA**

### **Visitantes Registrados**
```json
[
  {
    "nombre_completo": "Carlos Visitante",
    "documento": "12345678",
    "telefono": "+57 300 123 4567",
    "email": "carlos@email.com"
  },
  {
    "nombre_completo": "Ana María López", 
    "documento": "87654321",
    "telefono": "+57 310 987 6543",
    "email": "ana@email.com"
  }
]
```

### **Vehículos Registrados**
```json
[
  {
    "placa": "ABC123",
    "modelo": "Toyota Corolla",
    "color": "Blanco",
    "tipo": "automovil",
    "propietario": "residente1"
  },
  {
    "placa": "XYZ789",
    "modelo": "Chevrolet Spark", 
    "color": "Rojo",
    "tipo": "automovil",
    "propietario": "residente2"
  }
]
```

### **Visitas Programadas**
```json
[
  {
    "visitante": "Carlos Visitante",
    "propiedad": "101",
    "fecha_programada": "2025-10-02T15:00:00",
    "motivo": "Visita familiar",
    "estado": "PROGRAMADA"
  },
  {
    "visitante": "Ana María López",
    "propiedad": "201", 
    "fecha_programada": "2025-10-03T10:00:00",
    "motivo": "Servicio técnico",
    "estado": "PROGRAMADA"
  }
]
```

---

## 🔧 **DATOS DE MANTENIMIENTO DE PRUEBA**

### **Solicitudes de Mantenimiento**
```json
[
  {
    "titulo": "Reparación de toma eléctrica",
    "descripcion": "Toma eléctrica de la cocina no funciona",
    "propiedad": "101",
    "categoria": "ELECTRICIDAD",
    "prioridad": "ALTA",
    "estado": "PENDIENTE",
    "solicitante": "residente1"
  },
  {
    "titulo": "Goteo en baño principal",
    "descripcion": "La llave del lavamanos gotea constantemente", 
    "propiedad": "201",
    "categoria": "PLOMERIA",
    "prioridad": "MEDIA", 
    "estado": "EN_PROGRESO",
    "solicitante": "residente2",
    "asignado_a": "plomero1"
  },
  {
    "titulo": "Pintura de pared dañada",
    "descripcion": "Pared del salón necesita retoque de pintura",
    "propiedad": "101", 
    "categoria": "PINTURA",
    "prioridad": "BAJA",
    "estado": "COMPLETADA",
    "solicitante": "residente1",
    "asignado_a": "mantenimiento1"
  }
]
```

---

## 📱 **TOKENS DE DISPOSITIVOS PARA NOTIFICACIONES**

### **Tokens FCM de Prueba**
```json
[
  {
    "usuario": "residente1",
    "token": "fAKE_FCM_TOKEN_RESIDENTE1_ANDROID",
    "plataforma": "android",
    "activo": true
  },
  {
    "usuario": "admin",
    "token": "fAKE_FCM_TOKEN_ADMIN_IOS", 
    "plataforma": "ios",
    "activo": true
  },
  {
    "usuario": "seguridad1",
    "token": "fAKE_FCM_TOKEN_SEGURIDAD_WEB",
    "plataforma": "web", 
    "activo": true
  }
]
```

---

## 🧪 **FLUJOS DE PRUEBA COMPLETOS**

### **Flujo 1: Residente Consulta Finanzas**
```bash
1. Login: POST /api/login/ 
   Body: {"username": "residente1", "password": "isaelOrtiz2"}
   
2. Ver gastos: GET /api/finanzas/gastos/
   Headers: Authorization: Token <token>
   
3. Ver estado cuenta: GET /api/finanzas/estado-cuenta/
   Headers: Authorization: Token <token>
   
4. Ver multas: GET /api/finanzas/multas/
   Headers: Authorization: Token <token>
```

### **Flujo 2: Seguridad Gestiona Visita**
```bash
1. Login: POST /api/login/
   Body: {"username": "seguridad1", "password": "guardia123"}
   
2. Ver visitas: GET /api/seguridad/visitas/
   Headers: Authorization: Token <token>
   
3. Registrar ingreso: PUT /api/seguridad/visitas/{id}/
   Body: {"fecha_ingreso": "2025-10-02T15:05:00", "estado": "EN_CURSO"}
   
4. Registrar salida: PUT /api/seguridad/visitas/{id}/
   Body: {"fecha_salida": "2025-10-02T17:30:00", "estado": "FINALIZADA"}
```

### **Flujo 3: Mantenimiento Actualiza Solicitud**
```bash
1. Login: POST /api/login/
   Body: {"username": "electricista1", "password": "electrico123"}
   
2. Ver solicitudes asignadas: GET /api/mantenimiento/solicitudes/
   Headers: Authorization: Token <token>
   
3. Cambiar estado: POST /api/mantenimiento/solicitudes/{id}/cambiar_estado/
   Body: {"estado": "EN_PROGRESO"}
   
4. Completar trabajo: POST /api/mantenimiento/solicitudes/{id}/cambiar_estado/
   Body: {"estado": "COMPLETADA"}
```

### **Flujo 4: Admin Genera Expensas**
```bash
1. Login: POST /api/login/
   Body: {"username": "admin", "password": "admin123"}
   
2. Generar expensas: POST /api/finanzas/expensas/generar/
   Body: {
     "monto": 250000,
     "descripcion": "Administración Noviembre 2025",
     "fecha_vencimiento": "2025-11-30"
   }
   
3. Ver reporte: GET /api/finanzas/reportes/resumen/
   Headers: Authorization: Token <token>
```

---

## 🔧 **COMANDOS PARA CREAR USUARIOS (Para Backend)**

```python
# Script para crear todos los usuarios de prueba
# Ejecutar en Django shell: python manage.py shell

from django.contrib.auth.models import User
from usuarios.models import UserProfile, Residente
from condominio.models import Propiedad

# Crear usuarios si no existen
users_data = [
    {
        'username': 'admin',
        'password': 'admin123', 
        'email': 'admin@condominio.com',
        'first_name': 'Administrador',
        'last_name': 'Sistema',
        'role': 'PROPIETARIO',
        'is_staff': True,
        'is_superuser': True
    },
    {
        'username': 'residente1',
        'password': 'isaelOrtiz2',
        'email': 'residente1@gmail.com', 
        'first_name': 'Juan Carlos',
        'last_name': 'Pérez',
        'role': 'RESIDENTE'
    },
    {
        'username': 'residente2',
        'password': 'maria2024',
        'email': 'maria.garcia@gmail.com',
        'first_name': 'María',
        'last_name': 'García', 
        'role': 'RESIDENTE'
    },
    {
        'username': 'seguridad1',
        'password': 'guardia123',
        'email': 'seguridad@condominio.com',
        'first_name': 'Carlos',
        'last_name': 'Guardia',
        'role': 'SEGURIDAD'
    },
    {
        'username': 'electricista1', 
        'password': 'electrico123',
        'email': 'electricista@condominio.com',
        'first_name': 'Roberto',
        'last_name': 'Electricista',
        'role': 'MANTENIMIENTO',
        'especialidad': 'ELECTRICIDAD'
    },
    {
        'username': 'plomero1',
        'password': 'plomeria123', 
        'email': 'plomero@condominio.com',
        'first_name': 'Miguel',
        'last_name': 'Plomero',
        'role': 'MANTENIMIENTO',
        'especialidad': 'PLOMERIA'
    },
    {
        'username': 'mantenimiento1',
        'password': 'general123',
        'email': 'mantenimiento@condominio.com',
        'first_name': 'Luis',
        'last_name': 'Mantenimiento', 
        'role': 'MANTENIMIENTO',
        'especialidad': 'GENERAL'
    }
]

for user_data in users_data:
    username = user_data['username']
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(
            username=username,
            password=user_data['password'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            is_staff=user_data.get('is_staff', False),
            is_superuser=user_data.get('is_superuser', False)
        )
        
        # Crear perfil
        UserProfile.objects.create(
            user=user,
            role=user_data['role'],
            especialidad=user_data.get('especialidad', '')
        )
        
        print(f"✅ Usuario {username} creado exitosamente")
    else:
        print(f"⚠️ Usuario {username} ya existe")
```

---

## ✅ **VERIFICACIÓN DE USUARIOS**

### **Comandos de Verificación**
```bash
# Verificar que todos los usuarios existan
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"residente1","password":"isaelOrtiz2"}'

curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"seguridad1","password":"guardia123"}'
```

### **Respuesta Esperada (200 OK)**
```json
{
  "token": "abc123def456ghi789..."
}
```

---

## 📞 **INSTRUCCIONES PARA EL FRONTEND**

### **Configuración Base**
```javascript
const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Headers base para requests autenticados
const getAuthHeaders = (token) => ({
  'Content-Type': 'application/json',
  'Authorization': `Token ${token}`
});
```

### **Manejo de Roles**
```javascript
const ROLES = {
  PROPIETARIO: 'admin',
  RESIDENTE: 'residente', 
  SEGURIDAD: 'seguridad',
  MANTENIMIENTO: 'mantenimiento'
};

// Verificar permisos por rol
const hasPermission = (userRole, requiredRole) => {
  if (userRole === 'PROPIETARIO') return true; // Admin puede todo
  return userRole === requiredRole;
};
```

---

## 🎯 **RESUMEN PARA FRONTEND**

### **Usuarios Listos para Usar:**
- ✅ **admin** / admin123 (Acceso total)
- ✅ **residente1** / isaelOrtiz2 (Residente con datos)
- ✅ **residente2** / maria2024 (Segundo residente)
- ✅ **seguridad1** / guardia123 (Personal seguridad)
- ✅ **electricista1** / electrico123 (Mantenimiento eléctrico)
- ✅ **plomero1** / plomeria123 (Mantenimiento plomería)
- ✅ **mantenimiento1** / general123 (Mantenimiento general)

### **Datos de Prueba Disponibles:**
- ✅ Propiedades (3 apartamentos)
- ✅ Gastos y multas (para residente1)
- ✅ Visitantes y vehículos registrados
- ✅ Solicitudes de mantenimiento
- ✅ Tokens FCM para notificaciones

### **Backend Operativo:**
- 🌐 **URL:** http://127.0.0.1:8000/api/
- 📋 **Documentación:** http://127.0.0.1:8000/api/schema/swagger-ui/
- ✅ **Estado:** 100% funcional y listo para integración

---

**🚀 Todo listo para que el frontend inicie las pruebas de integración!**