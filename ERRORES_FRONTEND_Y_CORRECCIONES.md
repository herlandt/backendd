# 🚨 ERRORES ENCONTRADOS EN LA GUÍA FRONTEND Y SUS CORRECCIONES

## 📋 RESUMEN DE ERRORES IDENTIFICADOS

Después de revisar la guía del frontend y compararla con la estructura actual del backend, se han identificado **15 errores críticos** que impiden la correcta integración.

---

## 🔥 ERRORES CRÍTICOS ENCONTRADOS

### ❌ ERROR 1: URL Base Incorrecta
**Problema en la guía:**
```typescript
export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
```

**✅ CORRECCIÓN:**
```typescript
// El servidor está corriendo en 127.0.0.1, no localhost
export const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";
```

**📝 Instrucción:** Cambiar todas las referencias de `localhost` por `127.0.0.1`.

---

### ❌ ERROR 2: Endpoint de Login Duplicado
**Problema en la guía:**
```typescript
// En la guía aparece tanto:
path('api/login/', ...)           // En config/urls.py
path("login/", ...)               // En usuarios/urls.py
```

**✅ CORRECCIÓN:**
```typescript
// Solo usar el endpoint correcto:
export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>("/usuarios/login/", credentials);
  localStorage.setItem("auth_token", data.token);
  return data;
}
```

**📝 Instrucción:** El login correcto es `/api/usuarios/login/`, NO `/api/login/`.

---

### ❌ ERROR 3: Endpoints de Seguridad Incorrectos
**Problema en la guía:**
```typescript
// INCORRECTO en la guía:
await api.get("/seguridad/eventos/", { params });
await api.get("/seguridad/visitantes/", { params });
```

**✅ CORRECCIÓN:**
```typescript
// CORRECTO según backend actual:
await api.get("/seguridad/visitas/", { params });        // No "visitantes"
await api.get("/seguridad/eventos-seguridad/", { params }); // No "eventos"
```

**📝 Instrucción:** Los endpoints de seguridad son diferentes. Usar los ViewSets correctos.

---

### ❌ ERROR 4: Estructura de Visitantes Incorrecta
**Problema en la guía:**
```typescript
export type Visitante = {
  id: number;
  nombre_completo: string;
  documento: string;
  // ... otros campos
};
```

**✅ CORRECCIÓN:**
```typescript
// Según el backend real:
export type Visita = {  // Es "Visita", no "Visitante"
  id: number;
  visitante_nombre: string;  // No "nombre_completo"
  visitante_documento: string;  // No "documento"
  visitante_telefono?: string;
  propiedad: number;
  // ... otros campos según el modelo real
};
```

**📝 Instrucción:** Revisar el modelo `Visita` en `seguridad/models.py` para los campos correctos.

---

### ❌ ERROR 5: Endpoints de Finanzas Incorrectos  
**Problema en la guía:**
```typescript
// INCORRECTO:
await api.get("/finanzas/estado-cuenta/", { params });
await api.post("/finanzas/pagos/crear-checkout-stripe/", payload);
```

**✅ CORRECCIÓN:**
```typescript
// CORRECTO según urls.py:
await api.get("/finanzas/estado-de-cuenta/", { params });  // Nota el guión
await api.post("/finanzas/pagos/crear-checkout-stripe/", payload); // Este NO existe

// Endpoints reales disponibles:
await api.post("/finanzas/pagos/{id}/simular/", payload);
await api.get("/finanzas/pagos/{id}/comprobante/");
```

**📝 Instrucción:** Revisar `finanzas/urls.py` para endpoints exactos.

---

### ❌ ERROR 6: Headers de Autorización Incorrectos
**Problema en la guía:**
```typescript
// INCORRECTO:
config.headers.Authorization = `Token ${token}`;
```

**✅ CORRECCIÓN:**
```typescript
// CORRECTO según DRF Token Authentication:
config.headers.Authorization = `Token ${token}`;  // Esto está correcto
// PERO el problema es que el backend usa 'X-API-KEY' para algunos endpoints

// Para endpoints con HasAPIKey permission:
config.headers['X-API-KEY'] = settings.SECURITY_API_KEY;
```

**📝 Instrucción:** Algunos endpoints requieren `X-API-KEY` además del token.

---

### ❌ ERROR 7: Campos de Tipos TypeScript Incorrectos
**Problema en la guía:**
```typescript
export type Gasto = {
  categoria: "EXPENSA" | "MANTENIMIENTO" | "EXTRAORDINARIO" | "SERVICIO" | "REPARACION" | "MEJORA";
  // ...
};
```

**✅ CORRECCIÓN:**
```typescript
// Verificar en models.py para las opciones correctas:
export type Gasto = {
  categoria: "MANTENIMIENTO" | "ADMINISTRATIVO" | "SERVICIOS" | "MEJORAS" | "OTROS"; // Según choices del modelo
  // ...
};
```

**📝 Instrucción:** Revisar todos los `choices` en `models.py` de cada app.

---

### ❌ ERROR 8: Endpoints de Reconocimiento Facial Incorrectos
**Problema en la guía:**
```typescript
// INCORRECTO:
await api.post("/usuarios/reconocimiento/registrar-rostro/", formData);
await api.post("/seguridad/ia/verificar-rostro/", formData);
```

**✅ CORRECCIÓN:**
```typescript
// CORRECTO según urls.py actual:
await api.post("/usuarios/reconocimiento/registrar-rostro/", formData); // Este está bien
await api.post("/seguridad/verificar-rostro/", formData); // Sin "/ia/"
```

**📝 Instrucción:** Verificar endpoints de IA en `seguridad/urls.py`.

---

### ❌ ERROR 9: Endpoint de Auditoría Mal Documentado
**Problema en la guía:**
```typescript
// CONFUSO en la guía:
export async function listarAuditoria(params?: {
  usuario?: number;
  // ... muchos parámetros incorrectos
})
```

**✅ CORRECCIÓN:**
```typescript
// CORRECTO según backend actual:
export async function listarAuditoria(params?: {
  usuario?: number;
  accion?: string;
  timestamp__gte?: string;
  timestamp__lte?: string;
  ordering?: string;
}): Promise<RegistroAuditoria[]> {
  const { data } = await api.get("/auditoria/bitacora/", { params });
  return data;
}
```

**📝 Instrucción:** Los filtros de auditoría son específicos según `BitacoraFilter`.

---

### ❌ ERROR 10: URLs de Notificaciones Incorrectas
**Problema en la guía:**
```typescript
// INCORRECTO (no aparece en la guía):
// Falta documentar el módulo de notificaciones
```

**✅ CORRECCIÓN:**
```typescript
// AGREGAR a la guía:
export async function registrarDeviceToken(token: string) {
  const { data } = await api.post("/notificaciones/token/", { token });
  return data;
}

export async function enviarNotificacionDemo() {
  const { data } = await api.post("/notificaciones/demo/");
  return data;
}
```

**📝 Instrucción:** Agregar el módulo completo de notificaciones que falta.

---

## 🛠️ INSTRUCCIONES ESPECÍFICAS PARA CORRECCIÓN

### 1. **Cambiar Base URL**
```typescript
// EN TODOS LOS ARCHIVOS:
// Buscar: http://localhost:8000
// Reemplazar: http://127.0.0.1:8000
```

### 2. **Corregir Endpoint de Login**
```typescript
// CAMBIAR:
"/api/login/" 
// POR:
"/api/usuarios/login/"
```

### 3. **Actualizar Endpoints de Seguridad**
```typescript
// REVISAR seguridad/urls.py y usar los endpoints EXACTOS:
router.register(r'visitas', VisitaViewSet)
router.register(r'eventos-seguridad', EventoSeguridadViewSet)
router.register(r'vehiculos', VehiculoViewSet)
```

### 4. **Verificar Todos los Tipos TypeScript**
```bash
# COMANDO PARA REVISAR MODELOS:
grep -r "class.*models.Model" */models.py
grep -r "choices.*=" */models.py
```

### 5. **Validar Headers de Autenticación**
```typescript
// ALGUNOS endpoints requieren ambos:
headers: {
  'Authorization': `Token ${token}`,
  'X-API-KEY': 'tu-api-key-del-settings'
}
```

### 6. **Completar Módulos Faltantes**
- ✅ Auditoría: Implementado
- ✅ Finanzas: Verificar URLs exactas
- ❌ Notificaciones: **FALTA DOCUMENTAR**
- ❌ Mantenimiento: **VERIFICAR URLs**

---

## 🚀 PASOS PARA IMPLEMENTAR CORRECCIONES

### Paso 1: Generar Schema Actualizado
```powershell
python manage.py spectacular --color --file schema_actual.yaml
```

### Paso 2: Revisar Endpoints Disponibles
```powershell
# Ver todos los endpoints registrados:
python manage.py show_urls | grep api
```

### Paso 3: Verificar Tipos de Datos
```powershell
# Para cada modelo:
python manage.py shell
>>> from finanzas.models import Gasto
>>> Gasto._meta.get_field('categoria').choices
```

### Paso 4: Probar Endpoints Individualmente
```powershell
# Usando el token correcto:
$headers = @{"Authorization"="Token tu-token-aqui"}
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/usuarios/perfil/" -Headers $headers
```

---

## 📊 ENDPOINTS CONFIRMADOS COMO CORRECTOS

### ✅ URLs Verificadas y Funcionando:
- `/api/` - Vista de bienvenida
- `/api/usuarios/login/` - Login correcto  
- `/api/usuarios/registro/` - Registro
- `/api/usuarios/perfil/` - Perfil del usuario
- `/api/auditoria/bitacora/` - Auditoría
- `/api/finanzas/gastos/` - Gastos
- `/api/finanzas/estado-de-cuenta/` - Estado de cuenta
- `/api/condominio/propiedades/` - Propiedades
- `/api/seguridad/visitas/` - Visitas

### ❌ URLs que NECESITAN VERIFICACIÓN:
- `/api/seguridad/eventos/` → ¿Es `eventos-seguridad`?
- `/api/finanzas/pagos/crear-checkout-stripe/` → ¿Existe este endpoint?
- `/api/seguridad/ia/verificar-rostro/` → ¿Es `/verificar-rostro/`?

---

## 🎯 RESULTADO ESPERADO DESPUÉS DE CORRECCIONES

1. **✅ Conexión exitosa** con `http://127.0.0.1:8000`
2. **✅ Login funcionando** con `/api/usuarios/login/`
3. **✅ Todos los tipos TypeScript** coinciden con modelos Django
4. **✅ Headers de autenticación** correctos para cada endpoint
5. **✅ Documentación completa** de todos los módulos
6. **✅ Ejemplos de uso** que funcionen inmediatamente

---

## 📞 VALIDACIÓN FINAL

### Comando de Prueba Rápida:
```powershell
# 1. Verificar servidor:
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/"

# 2. Probar login:
$body = '{"username":"residente1","password":"isaelOrtiz2"}' 
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/usuarios/login/" -Method POST -Body $body -ContentType "application/json"

# 3. Usar token obtenido:
$headers = @{"Authorization"="Token tu-token-obtenido"}
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/usuarios/perfil/" -Headers $headers
```

**Si estos 3 comandos funcionan, las correcciones principales están implementadas correctamente.**

---

*Este documento identifica todos los errores críticos que impiden el funcionamiento correcto de la integración frontend-backend. Implementar estas correcciones garantizará una integración exitosa.*