# 🚀 INICIO RÁPIDO - FRONTEND

**⏱️ Tiempo de lectura: 2 minutos**  
**🎯 Objetivo: Conectar su frontend al backend inmediatamente**

---

## 🔥 **CREDENCIALES QUE FUNCIONAN:**

```
👨‍💼 ADMIN:     admin / admin123
🏠 RESIDENTE:  residente1 / isaelOrtiz2  
🛡️ SEGURIDAD:  seguridad1 / guardia123
🔧 TÉCNICO:    electricista1 / tecnico123
```

---

## ⚡ **CONEXIÓN INMEDIATA:**

### **📱 En su código Flutter/JavaScript:**
```javascript
// URL BASE (cambiar según su dispositivo)
const API_URL = 'http://127.0.0.1:8000/api';  // Localhost
// const API_URL = 'http://10.0.2.2:8000/api';     // Android AVD
// const API_URL = 'http://192.168.0.5:8000/api';  // Dispositivo físico

// Para React/Web (Vite usa puerto 5173 por defecto)
const API_URL = 'http://127.0.0.1:8000/api';  // ✅ CORS ya configurado

// LOGIN INMEDIATO
fetch(`${API_URL}/login/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  })
})
.then(response => response.json())
.then(data => {
  console.log('Token:', data.token);
  // Guardar data.token para próximas requests
});
```

### **🌐 CORS YA CONFIGURADO:**
✅ Backend configurado para aceptar peticiones desde:
- `http://localhost:5173` (Vite/React)
- `http://localhost:3000` (Create React App)
- `http://127.0.0.1:5173` (Alternativa localhost)
- `http://127.0.0.1:3000` (Alternativa localhost)

---

## 🧪 **PRUEBA RÁPIDA:**

### **Copiar y pegar en terminal/cmd:**
```bash
curl -X POST http://127.0.0.1:8000/api/login/ -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```

**✅ Resultado esperado:** `{"token":"algún-token-aquí"}`

---

## 📋 **ENDPOINTS LISTOS:**

```
🔐 POST /api/login/          - Login
👤 GET  /api/usuarios/perfil/ - Perfil usuario
🏢 GET  /api/condominios/     - Lista condominios  
🏠 GET  /api/propiedades/     - Lista propiedades
🚪 GET  /api/controles-acceso/ - Control acceso
💰 GET  /api/gastos/          - Gastos
💰 GET  /api/pagos/           - Pagos
📢 GET  /api/avisos/          - Avisos
🔧 GET  /api/tickets/         - Tickets mantenimiento
```

**⚠️ Importante:** Agregar header `Authorization: Token su-token-aquí` después del login

---

## 🎯 **SIGUIENTES PASOS:**

1. **✅ Hacer login con admin/admin123**
2. **✅ Obtener token**  
3. **✅ Usar token en próximas requests**
4. **✅ Probar endpoints de su interés**
5. **✅ Desarrollar UI según respuestas del backend**

---

## 📖 **DOCUMENTACIÓN COMPLETA:**

- **📄 USUARIOS_PRUEBA_FRONTEND.md** - Todos los usuarios y ejemplos
- **📄 RESPUESTA_FINAL_FRONTEND.md** - Análisis de su documentación  
- **📄 ENTREGA_COMPLETA_FRONTEND.md** - Entrega completa con todo el detalle
- **🌐 Swagger UI:** http://127.0.0.1:8000/api/schema/swagger-ui/

---

## 🆘 **SI ALGO NO FUNCIONA:**

### **❌ Error de conexión:**
- Verificar que Django esté corriendo: `python manage.py runserver`
- Cambiar 127.0.0.1 por la IP correcta de su máquina

### **❌ Error 401/403:**
- Verificar credenciales: exactamente `admin` y `admin123`
- Verificar header Authorization: `Token su-token-aquí`

### **❌ Error 404:**
- Verificar URL: debe incluir `/api/` en la ruta

---

**🎉 ¡Listo! Con esto pueden conectarse inmediatamente.**

**📞 Cualquier duda: revisar documentación completa en los otros archivos MD.**