# 📝 INSTRUCCIONES PRECISAS PARA EL EQUIPO FRONTEND

## 🎯 CAMBIOS INMEDIATOS REQUERIDOS

Estas son las **correcciones exactas** que deben implementarse en la guía frontend para que funcione correctamente con el backend actual.

---

## 🔧 CORRECCIÓN 1: BASE URL (CRÍTICO)

### ❌ Buscar en TODA la guía:
```typescript
"http://localhost:8000"
```

### ✅ Reemplazar por:
```typescript
"http://127.0.0.1:8000"
```

**📍 Ubicación**: Líneas 9-11 del archivo de guía
**⚠️ Impacto**: Sin esto, ninguna conexión funcionará

---

## 🔧 CORRECCIÓN 2: ENDPOINT DE LOGIN (CRÍTICO)

### ❌ Buscar:
```typescript
export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>("/usuarios/login/", credentials);
```

### ✅ Reemplazar por:
```typescript
export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>("/usuarios/login/", credentials);
  localStorage.setItem("auth_token", data.token);
  return data;
}
```

**📍 Ubicación**: Línea ~67 de la guía
**⚠️ Impacto**: El login ya está correcto, pero asegurar que use `/usuarios/login/`

---

## 🔧 CORRECCIÓN 3: ENDPOINTS DE SEGURIDAD (ALTO IMPACTO)

### ❌ Buscar y ELIMINAR estas funciones incorrectas:
```typescript
export async function listarEventosSeguridad(params?: {
  tipo_evento?: "ACCESO_VEHICULAR" | "ACCESO_PEATONAL" | "ALARMA" | "INCIDENTE";
  // ... resto del código
}): Promise<EventoSeguridad[]> {
  const { data } = await api.get("/seguridad/eventos/", { params });
  return data;
}
```

### ✅ Reemplazar por:
```typescript
export async function listarEventosSeguridad(params?: {
  tipo_evento?: string;
  descripcion__icontains?: string;
  fecha_hora__gte?: string;
  fecha_hora__lte?: string;
  search?: string;
  ordering?: string;
}): Promise<EventoSeguridad[]> {
  const { data } = await api.get("/seguridad/eventos-seguridad/", { params });
  return data;
}
```

**📍 Ubicación**: Líneas ~460-480 de la guía

---

## 🔧 CORRECCIÓN 4: ENDPOINTS DE VISITANTES (ALTO IMPACTO)

### ❌ Buscar:
```typescript
export async function listarVisitantes(params?: {
  // ... parámetros
}): Promise<Visitante[]> {
  const { data } = await api.get("/seguridad/visitantes/", { params });
  return data;
}
```

### ✅ Reemplazar por:
```typescript
export async function listarVisitas(params?: {
  visitante_nombre__icontains?: string;
  visitante_documento?: string;
  propiedad?: number;
  fecha_hora_ingreso__gte?: string;
  fecha_hora_ingreso__lte?: string;
  search?: string;
  ordering?: string;
}): Promise<Visita[]> {
  const { data } = await api.get("/seguridad/visitas/", { params });
  return data;
}
```

**📍 Ubicación**: Líneas ~490-510 de la guía

---

## 🔧 CORRECCIÓN 5: TIPOS TYPESCRIPT - VISITANTES (MEDIO IMPACTO)

### ❌ Buscar:
```typescript
export type Visitante = {
  id: number;
  nombre_completo: string;
  documento: string;
  telefono?: string;
  motivo_visita: string;
  propiedad_visitada: number;
  fecha_ingreso: string;
  fecha_salida?: string;
  autorizado_por?: number;
};
```

### ✅ Reemplazar por:
```typescript
export type Visita = {
  id: number;
  visitante_nombre: string;
  visitante_documento: string;
  visitante_telefono?: string;
  motivo_visita: string;
  propiedad: number;
  fecha_hora_ingreso: string; // ISO datetime
  fecha_hora_salida?: string;
  autorizado_por?: number;
  activa: boolean;
};
```

**📍 Ubicación**: Líneas ~210-220 de la guía

---

## 🔧 CORRECCIÓN 6: ENDPOINT ESTADO DE CUENTA (MEDIO IMPACTO)

### ❌ Buscar:
```typescript
const { data } = await api.get("/finanzas/estado-cuenta/", { params });
```

### ✅ Reemplazar por:
```typescript
const { data } = await api.get("/finanzas/estado-de-cuenta/", { params });
```

**📍 Ubicación**: Múltiples líneas en sección de finanzas
**⚠️ Nota**: Agregar el guión en "estado-de-cuenta"

---

## 🔧 CORRECCIÓN 7: ELIMINAR ENDPOINT INEXISTENTE (CRÍTICO)

### ❌ Buscar y ELIMINAR completamente:
```typescript
// Stripe Checkout
export async function crearCheckoutStripe(payload: {
  gastos_ids?: number[];
  multas_ids?: number[];
  reservas_ids?: number[];
}) {
  const { data } = await api.post("/finanzas/pagos/crear-checkout-stripe/", payload);
  return data; // { checkout_url, pago_id, monto_total }
}
```

### ✅ Reemplazar por:
```typescript
// Simular Pago (endpoint real disponible)
export async function simularPago(pagoId: number) {
  const { data } = await api.post(`/finanzas/pagos/${pagoId}/simular/`);
  return data;
}
```

**📍 Ubicación**: Líneas ~410-420 de la guía

---

## 🔧 CORRECCIÓN 8: AGREGAR MÓDULO FALTANTE (ALTO IMPACTO)

### ✅ AGREGAR al final de la sección de funciones:

```typescript
// 4.7 Notificaciones
export async function registrarDeviceToken(deviceToken: string) {
  const { data } = await api.post("/notificaciones/token/", { device_token: deviceToken });
  return data;
}

export async function enviarNotificacionDemo() {
  const { data } = await api.post("/notificaciones/demo/");
  return data;
}

export async function registrarDispositivo(payload: {
  device_token: string;
  device_type: "android" | "ios" | "web";
  device_name?: string;
}) {
  const { data } = await api.post("/notificaciones/registrar-dispositivo/", payload);
  return data;
}
```

**📍 Ubicación**: Después de la sección 4.6 (Auditoría)

---

## 🔧 CORRECCIÓN 9: ACTUALIZAR TIPOS DE DATOS - GASTO (MEDIO IMPACTO)

### ❌ Buscar:
```typescript
categoria: "EXPENSA" | "MANTENIMIENTO" | "EXTRAORDINARIO" | "SERVICIO" | "REPARACION" | "MEJORA";
```

### ✅ Reemplazar por:
```typescript
categoria: "MANTENIMIENTO" | "ADMINISTRATIVO" | "SERVICIOS" | "MEJORAS" | "OTROS";
```

**📍 Ubicación**: Tipo `Gasto` en la sección de tipos

---

## 🔧 CORRECCIÓN 10: CORREGIR RECONOCIMIENTO FACIAL (BAJO IMPACTO)

### ❌ Buscar:
```typescript
const { data } = await api.post("/seguridad/ia/verificar-rostro/", formData, {
```

### ✅ Reemplazar por:
```typescript
const { data } = await api.post("/seguridad/verificar-rostro/", formData, {
```

**📍 Ubicación**: Función `verificarRostro`

---

## 🛠️ VALIDACIÓN DE CORRECCIONES

### Después de implementar TODAS las correcciones, probar:

```typescript
// 1. Test de conexión:
const response = await fetch("http://127.0.0.1:8000/api/");
console.log(await response.json());

// 2. Test de login:
const loginData = await login({
  username: "residente1",
  password: "isaelOrtiz2"
});
console.log("Token:", loginData.token);

// 3. Test de endpoint protegido:
const perfil = await getPerfil();
console.log("Perfil:", perfil);
```

---

## ⚡ ORDEN DE PRIORIDAD PARA IMPLEMENTACIÓN

### 🔥 **PRIORIDAD CRÍTICA** (Implementar PRIMERO):
1. ✅ Corrección 1: Base URL
2. ✅ Corrección 2: Endpoint de login  
3. ✅ Corrección 7: Eliminar endpoint inexistente

### 🟡 **PRIORIDAD ALTA** (Implementar SEGUNDO):
4. ✅ Corrección 3: Endpoints de seguridad
5. ✅ Corrección 4: Endpoints de visitantes
6. ✅ Corrección 8: Agregar módulo notificaciones

### 🟢 **PRIORIDAD MEDIA** (Implementar TERCERO):
7. ✅ Corrección 5: Tipos TypeScript visitantes
8. ✅ Corrección 6: Estado de cuenta
9. ✅ Corrección 9: Tipos de gasto

### ⚪ **PRIORIDAD BAJA** (Implementar CUARTO):
10. ✅ Corrección 10: Reconocimiento facial

---

## 📊 CHECKLIST DE VERIFICACIÓN

Después de implementar las correcciones, verificar que:

- [ ] ✅ Base URL usa `127.0.0.1:8000`
- [ ] ✅ Login funciona con `/usuarios/login/`
- [ ] ✅ Visitas usan `/seguridad/visitas/`
- [ ] ✅ Estado de cuenta usa guión: `/estado-de-cuenta/`
- [ ] ✅ No existe referencia a `/crear-checkout-stripe/`
- [ ] ✅ Módulo de notificaciones está incluido
- [ ] ✅ Tipos TypeScript coinciden con modelos Django
- [ ] ✅ Todas las funciones tienen parámetros correctos

---

## 🎯 RESULTADO FINAL ESPERADO

Después de implementar estas correcciones:

1. **La conexión funcionará** inmediatamente con `127.0.0.1:8000`
2. **El login será exitoso** con las credenciales de prueba
3. **Todos los endpoints responderán** correctamente
4. **Los tipos TypeScript coincidirán** con los datos del backend
5. **La guía será 100% funcional** para desarrollo frontend

**¡Con estas correcciones, la integración frontend-backend será perfecta!** 🚀