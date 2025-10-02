# 🚀 INSTRUCCIONES: SCRIPT DE USUARIOS DE PRUEBA PARA FRONTEND

**📅 Fecha:** Octubre 2, 2025  
**🎯 Para:** Equipo Frontend Web/Móvil  
**📄 Archivo:** `crear_usuarios_frontend.py`

---

## 📋 **¿QUÉ HACE ESTE SCRIPT?**

El script `crear_usuarios_frontend.py` crea automáticamente todos los usuarios de prueba que el frontend necesita para desarrollar y probar la aplicación.

### **✅ USUARIOS QUE CREA:**
1. **👨‍💼 admin / admin123** - Administrador principal
2. **🏠 residente1 / isaelOrtiz2** - Residente principal  
3. **🏠 residente2 / maria123** - Residente secundario
4. **🛡️ seguridad1 / guardia123** - Personal de seguridad
5. **🔧 electricista1 / tecnico123** - Técnico electricista
6. **🔧 plomero1 / plomero123** - Técnico plomero
7. **🔧 mantenimiento1 / mant123** - Mantenimiento general

---

## 🔧 **CÓMO USAR EL SCRIPT (FRONTEND)**

### **📋 PRERREQUISITOS:**
1. ✅ Tener el backend clonado y configurado
2. ✅ Python y Django instalados
3. ✅ Base de datos configurada
4. ✅ Migraciones aplicadas

### **⚡ PASOS RÁPIDOS:**

#### **1. Navegar a la carpeta del backend:**
```bash
cd ruta/del/backend
# Ejemplo: cd C:\Users\tu-usuario\Documents\backendd
```

#### **2. Ejecutar el script:**
```bash
python crear_usuarios_frontend.py
```

#### **3. ¡Listo! Verás una salida como esta:**
```
============================================================
🚀 CREADOR DE USUARIOS DE PRUEBA PARA FRONTEND
============================================================
📅 Fecha: Octubre 2, 2025
🎯 Propósito: Crear usuarios para testing del frontend
💻 Para: Equipo Frontend Web/Móvil
============================================================

👥 Creando usuarios de prueba...

✅ CREADO Usuario: admin / admin123
   📧 Email: admin@condominio.com
   👤 Nombre: Administrador Sistema
   🏷️ Rol: PROPIETARIO

[... más usuarios ...]

🎉 ¡USUARIOS DE PRUEBA CREADOS EXITOSAMENTE!
```

---

## 🧪 **PROBAR QUE FUNCIONÓ**

### **🔐 Test de Login Rápido:**
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### **✅ Respuesta Esperada:**
```json
{"token":"tu-token-aquí"}
```

### **📱 En tu App Frontend:**
```javascript
// Ejemplo en JavaScript/React
const loginTest = async () => {
  const response = await fetch('http://127.0.0.1:8000/api/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username: 'admin',
      password: 'admin123'
    })
  });
  
  const data = await response.json();
  console.log('Token:', data.token);
};
```

---

## 👥 **USUARIOS DISPONIBLES DESPUÉS DEL SCRIPT**

### **👨‍💼 ADMINISTRADOR (Acceso completo):**
```
Usuario: admin
Contraseña: admin123
Rol: PROPIETARIO
Acceso: Todos los módulos del sistema
```

### **🏠 RESIDENTES (Acceso limitado):**
```
Usuario: residente1          Usuario: residente2
Contraseña: isaelOrtiz2      Contraseña: maria123
Rol: RESIDENTE               Rol: RESIDENTE
Acceso: Finanzas, avisos     Acceso: Finanzas, avisos
```

### **🛡️ SEGURIDAD (Módulo seguridad):**
```
Usuario: seguridad1
Contraseña: guardia123
Rol: SEGURIDAD
Especialidad: GUARDIA_PRINCIPAL
Acceso: Control de acceso, alertas, visitantes
```

### **🔧 MANTENIMIENTO (Tickets y reparaciones):**
```
Usuario: electricista1       Usuario: plomero1           Usuario: mantenimiento1
Contraseña: tecnico123       Contraseña: plomero123      Contraseña: mant123
Rol: MANTENIMIENTO           Rol: MANTENIMIENTO          Rol: MANTENIMIENTO
Especialidad: ELECTRICISTA   Especialidad: PLOMERO       Especialidad: GENERAL
```

---

## 🌐 **ENDPOINTS LISTOS PARA PROBAR**

### **🔐 Autenticación:**
```
POST /api/login/                    # Iniciar sesión
GET  /api/usuarios/perfil/          # Perfil del usuario actual
```

### **👥 Gestión de Usuarios:**
```
GET  /api/usuarios/                 # Lista usuarios (solo admin)
```

### **🏠 Propiedades:**
```
GET  /api/propiedades/              # Lista propiedades
```

### **💰 Finanzas:**
```
GET  /api/pagos/                    # Lista pagos
GET  /api/gastos/                   # Lista gastos
```

### **📢 Comunicación:**
```
GET  /api/avisos/                   # Lista avisos
```

### **🛡️ Seguridad:**
```
GET  /api/controles-acceso/         # Control de acceso
GET  /api/visitantes/               # Gestión visitantes
```

### **🔧 Mantenimiento:**
```
GET  /api/tickets/                  # Tickets de mantenimiento
```

---

## 🔍 **DOCUMENTACIÓN AUTOMÁTICA**

### **📖 Swagger UI:**
http://127.0.0.1:8000/api/schema/swagger-ui/

### **📖 ReDoc:**
http://127.0.0.1:8000/api/schema/redoc/

### **📄 Schema OpenAPI:**
http://127.0.0.1:8000/api/schema/

---

## ❓ **TROUBLESHOOTING**

### **❌ Error: "No module named 'django'"**
```bash
# Activar entorno virtual del backend
cd ruta/del/backend
source venv/bin/activate  # Linux/Mac
# O en Windows:
venv\Scripts\activate
```

### **❌ Error: "django.core.exceptions.ImproperlyConfigured"**
```bash
# Verificar que estés en la carpeta del backend
cd ruta/del/backend
python manage.py check
```

### **❌ Error: "relation does not exist"**
```bash
# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate
```

### **❌ Error: "Permission denied"**
```bash
# En Linux/Mac, dar permisos al script
chmod +x crear_usuarios_frontend.py
```

---

## 🎯 **CASOS DE USO PARA FRONTEND**

### **📱 Testing de Login:**
- Probar con cada tipo de usuario
- Verificar que cada rol accede a sus módulos correspondientes
- Confirmar que tokens se generan correctamente

### **🧪 Testing de Funcionalidades:**
- **Admin:** Gestión completa de usuarios, finanzas, configuración
- **Residentes:** Ver sus pagos, crear solicitudes, ver avisos
- **Seguridad:** Control de acceso, registro de visitantes
- **Mantenimiento:** Gestión de tickets, asignaciones

### **🔐 Testing de Permisos:**
- Verificar que cada usuario solo accede a lo permitido
- Confirmar que endpoints protegidos requieren autenticación
- Probar que roles específicos tienen acceso limitado

---

## 📞 **SOPORTE**

### **✅ Si el script funciona correctamente:**
- Todos los usuarios están listos para usar
- Puedes empezar a desarrollar inmediatamente
- Las credenciales están verificadas y funcionando

### **❌ Si tienes problemas:**
1. Verificar que el backend esté corriendo
2. Confirmar que las migraciones estén aplicadas
3. Revisar que la base de datos sea accesible
4. Contactar al equipo backend si persisten errores

---

## 🎉 **¡LISTO PARA DESARROLLAR!**

**Con estos usuarios de prueba, el frontend puede:**
- ✅ Probar todos los flujos de autenticación
- ✅ Desarrollar interfaces específicas por rol
- ✅ Testing completo de todas las funcionalidades
- ✅ Integración total con el backend
- ✅ Demos y presentaciones con datos reales

**🚀 ¡A desarrollar se ha dicho!**