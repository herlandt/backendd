# Guía de Integración Frontend — Condominio API (v1.0.0) - VERSIÓN FINAL

> **Objetivo**: Guía **100% actualizada** con el sistema completo de auditoría automática y notificaciones inteligentes. Incluye todos los endpoints funcionales, autenticación, filtros avanzados, subida de archivos, y el sistema de eventos automático implementado.

---

## 1) Base URL y Configuración

- **Base URL**: `http://localhost:8000` (desarrollo) o `https://tu-dominio.com` (producción)
- **Prefijo**: Todos los endpoints comienzan con `/api/`
- **Versión**: OpenAPI 3.0.3, API v1.0.0

```typescript
export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
export const API_BASE = `${API_URL}/api`;
```

---

## 2) Autenticación (Token Authentication)

### Configuración de Axios con Interceptores
```typescript
import axios from "axios";

export const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: { "Content-Type": "application/json" },
});

// Interceptor para inyectar token automáticamente
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("auth_token");
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Interceptor para manejo de errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    if (status === 401) {
      localStorage.removeItem("auth_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);
```

### Login y Registro
```typescript
// Tipos
type LoginRequest = {
  username: string;
  password: string;
};

type LoginResponse = {
  token: string;
};

type RegistroRequest = {
  username: string;
  password: string;
  email: string;
  first_name: string;
  last_name: string;
  telefono?: string;
  es_residente?: boolean;
};

// Funciones de autenticación
export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>("/usuarios/login/", credentials);
  localStorage.setItem("auth_token", data.token);
  return data;
}

export async function registro(userData: RegistroRequest) {
  const { data } = await api.post("/usuarios/registro/", userData);
  return data;
}

export function logout() {
  localStorage.removeItem("auth_token");
  window.location.href = "/login";
}
```

---

## 3) Tipos de Datos (TypeScript)

```typescript
// Usuarios
export type Residente = {
  id: number;
  user: number;
  telefono?: string;
  fecha_nacimiento?: string;
  user_detail?: {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
  };
};

// Condominio
export type AreaComun = {
  id: number;
  nombre: string;
  descripcion?: string;
  capacidad: number;
  costo_reserva: string; // Decimal como string
  disponible: boolean;
  horario_apertura?: string; // HH:mm:ss
  horario_cierre?: string; // HH:mm:ss
  reglas?: string;
};

export type Propiedad = {
  id: number;
  numero: string;
  torre?: string;
  residente?: number;
  telefono_contacto?: string;
  observaciones?: string;
};

export type Regla = {
  id: number;
  titulo: string;
  descripcion: string;
  categoria: "FINANZAS" | "GENERAL" | "MANTENIMIENTO" | "SEGURIDAD";
  activa: boolean;
  fecha_creacion: string;
};

// Finanzas
export type Gasto = {
  id: number;
  monto: string; // Decimal como string
  fecha_emision: string; // YYYY-MM-DD
  fecha_vencimiento?: string;
  descripcion: string;
  categoria: "EXPENSA" | "MANTENIMIENTO" | "EXTRAORDINARIO" | "SERVICIO" | "REPARACION" | "MEJORA";
  pagado: boolean;
  mes: number;
  anio: number;
  propiedad: number;
};

export type Multa = {
  id: number;
  concepto: string;
  monto: string;
  fecha_emision: string;
  fecha_vencimiento?: string;
  descripcion: string;
  pagado: boolean;
  mes: number;
  anio: number;
  propiedad: number;
  creado_por?: number;
};

export type Reserva = {
  id: number;
  area_comun: number;
  usuario: number;
  fecha_reserva: string; // YYYY-MM-DD
  hora_inicio: string; // HH:mm:ss
  hora_fin: string; // HH:mm:ss
  estado: "SOLICITADA" | "CONFIRMADA" | "PAGADA" | "CANCELADA";
  costo?: string;
  observaciones?: string;
  area_comun_detail?: AreaComun;
};

export type Pago = {
  id: number;
  usuario: number;
  monto_total: string;
  fecha_pago: string; // ISO datetime
  estado_pago: "PENDIENTE" | "PAGADO" | "FALLIDO" | "CANCELADO";
  metodo_pago: "STRIPE" | "PAGOSNET" | "EFECTIVO" | "TRANSFERENCIA";
  id_transaccion_pasarela?: string;
  comprobante?: string;
  qr_data?: string;
};

// Seguridad
export type EventoSeguridad = {
  id: number;
  tipo_evento: "ACCESO_VEHICULAR" | "ACCESO_PEATONAL" | "ALARMA" | "INCIDENTE";
  descripcion: string;
  fecha_hora: string; // ISO datetime
  ubicacion?: string;
  accion: "PERMITIR" | "DENEGAR" | "ALERTAR";
  motivo?: string;
  usuario_responsable?: number;
  resuelto: boolean;
};

export type Visitante = {
  id: number;
  nombre_completo: string;
  documento: string;
  telefono?: string;
  motivo_visita: string;
  propiedad_visitada: number;
  fecha_ingreso: string; // ISO datetime
  fecha_salida?: string;
  autorizado_por?: number;
};

// Mantenimiento
export type SolicitudMantenimiento = {
  id: number;
  titulo: string;
  descripcion: string;
  categoria: "PLOMERIA" | "ELECTRICIDAD" | "LIMPIEZA" | "JARDINERIA" | "PINTURA" | "OTRO";
  prioridad: "BAJA" | "MEDIA" | "ALTA" | "URGENTE";
  estado: "PENDIENTE" | "EN_PROGRESO" | "COMPLETADA" | "CANCELADA";
  solicitante: number;
  asignado_a?: number;
  fecha_solicitud: string;
  fecha_resolucion?: string;
  costo_estimado?: string;
  observaciones?: string;
};
```

---

## 4) Funciones de API por Módulo

### 4.1 Usuarios y Perfil
```typescript
export async function getPerfil(): Promise<Residente> {
  const { data } = await api.get("/usuarios/perfil/");
  return data;
}

export async function actualizarPerfil(perfil: Partial<Residente>) {
  const { data } = await api.put("/usuarios/perfil/", perfil);
  return data;
}

export async function listarResidentes(params?: {
  search?: string;
  ordering?: string;
}) {
  const { data } = await api.get("/usuarios/residentes/", { params });
  return data;
}
```

### 4.2 Reconocimiento Facial
```typescript
export async function registrarRostro(file: File) {
  const formData = new FormData();
  formData.append("foto", file);
  
  const { data } = await api.post("/usuarios/reconocimiento/registrar-rostro/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function verificarRostro(file: File) {
  const formData = new FormData();
  formData.append("foto", file);
  
  const { data } = await api.post("/seguridad/ia/verificar-rostro/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}
```

### 4.3 Condominio
```typescript
export async function listarAreasComunes(params?: {
  nombre__icontains?: string;
  capacidad?: number;
  capacidad__gte?: number;
  capacidad__lte?: number;
  costo_reserva?: number;
  costo_reserva__gte?: number;
  costo_reserva__lte?: number;
  search?: string;
  ordering?: string;
}): Promise<AreaComun[]> {
  const { data } = await api.get("/condominio/areas-comunes/", { params });
  return data;
}

export async function getAreaComun(id: number): Promise<AreaComun> {
  const { data } = await api.get(`/condominio/areas-comunes/${id}/`);
  return data;
}

export async function listarPropiedades(params?: {
  numero__icontains?: string;
  torre?: string;
  search?: string;
  ordering?: string;
}): Promise<Propiedad[]> {
  const { data } = await api.get("/condominio/propiedades/", { params });
  return data;
}

export async function listarReglas(params?: {
  categoria?: "FINANZAS" | "GENERAL" | "MANTENIMIENTO" | "SEGURIDAD";
  activa?: boolean;
  search?: string;
  ordering?: string;
}): Promise<Regla[]> {
  const { data } = await api.get("/condominio/reglas/", { params });
  return data;
}
```

### 4.4 Finanzas
```typescript
export async function getEstadoCuentaUnificado() {
  const { data } = await api.get("/finanzas/estado-cuenta-unificado/");
  return data;
}

export async function listarGastos(params?: {
  anio?: number;
  mes?: number;
  categoria?: string;
  pagado?: boolean;
  propiedad?: number;
  monto__gte?: number;
  monto__lte?: number;
  fecha_emision__gte?: string;
  fecha_emision__lte?: string;
  search?: string;
  ordering?: string;
}): Promise<Gasto[]> {
  const { data } = await api.get("/finanzas/gastos/", { params });
  return data;
}

export async function listarMultas(params?: {
  anio?: number;
  mes?: number;
  concepto__icontains?: string;
  pagado?: boolean;
  propiedad?: number;
  monto__gte?: number;
  monto__lte?: number;
  search?: string;
  ordering?: string;
}): Promise<Multa[]> {
  const { data } = await api.get("/finanzas/multas/", { params });
  return data;
}

export async function listarReservas(params?: {
  usuario?: number;
  area_comun?: number;
  estado?: "SOLICITADA" | "CONFIRMADA" | "PAGADA" | "CANCELADA";
  fecha_reserva?: string;
  fecha_reserva__gte?: string;
  fecha_reserva__lte?: string;
  search?: string;
  ordering?: string;
}): Promise<Reserva[]> {
  const { data } = await api.get("/finanzas/reservas/", { params });
  return data;
}

export async function crearReserva(reserva: {
  area_comun: number;
  fecha_reserva: string;
  hora_inicio: string;
  hora_fin: string;
  observaciones?: string;
}): Promise<Reserva> {
  const { data } = await api.post("/finanzas/reservas/", reserva);
  return data;
}

export async function confirmarReserva(id: number): Promise<Reserva> {
  const { data } = await api.post(`/finanzas/reservas/${id}/confirmar/`);
  return data;
}

export async function pagarReserva(id: number) {
  const { data } = await api.post(`/finanzas/reservas/${id}/pagar/`);
  return data;
}

export async function listarPagos(params?: {
  usuario?: number;
  estado_pago?: string;
  metodo_pago?: string;
  fecha_pago__gte?: string;
  fecha_pago__lte?: string;
  search?: string;
  ordering?: string;
}): Promise<Pago[]> {
  const { data } = await api.get("/finanzas/pagos/", { params });
  return data;
}

// Stripe Checkout
export async function crearCheckoutStripe(payload: {
  gastos_ids?: number[];
  multas_ids?: number[];
  reservas_ids?: number[];
}) {
  const { data } = await api.post("/finanzas/pagos/crear-checkout-stripe/", payload);
  return data; // { checkout_url, pago_id, monto_total }
}

// Descargar comprobante PDF
export async function descargarComprobante(pagoId: number) {
  const response = await api.get(`/finanzas/pagos/${pagoId}/comprobante/`, {
    responseType: "blob",
  });
  
  const blob = new Blob([response.data], { type: "application/pdf" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `comprobante_${pagoId}.pdf`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
```

### 4.5 Seguridad
```typescript
export async function controlAccesoVehicular(placa: string) {
  const { data } = await api.post("/seguridad/control-acceso-vehicular/", { placa });
  return data;
}

export async function controlSalidaVehicular(placa: string) {
  const { data } = await api.post("/seguridad/control-salida-vehicular/", { placa });
  return data;
}

export async function listarEventosSeguridad(params?: {
  tipo_evento?: "ACCESO_VEHICULAR" | "ACCESO_PEATONAL" | "ALARMA" | "INCIDENTE";
  accion?: "PERMITIR" | "DENEGAR" | "ALERTAR";
  resuelto?: boolean;
  fecha_hora__gte?: string;
  fecha_hora__lte?: string;
  search?: string;
  ordering?: string;
}): Promise<EventoSeguridad[]> {
  const { data } = await api.get("/seguridad/eventos/", { params });
  return data;
}

export async function crearEventoSeguridad(evento: {
  tipo_evento: string;
  descripcion: string;
  ubicacion?: string;
  accion: string;
  motivo?: string;
}): Promise<EventoSeguridad> {
  const { data } = await api.post("/seguridad/eventos/", evento);
  return data;
}

export async function listarVisitantes(params?: {
  nombre_completo__icontains?: string;
  documento?: string;
  documento__icontains?: string;
  propiedad_visitada?: number;
  fecha_ingreso__gte?: string;
  fecha_ingreso__lte?: string;
  search?: string;
  ordering?: string;
}): Promise<Visitante[]> {
  const { data } = await api.get("/seguridad/visitantes/", { params });
  return data;
}

export async function registrarVisitante(visitante: {
  nombre_completo: string;
  documento: string;
  telefono?: string;
  motivo_visita: string;
  propiedad_visitada: number;
}): Promise<Visitante> {
  const { data } = await api.post("/seguridad/visitantes/", visitante);
  return data;
}

// Export CSV de visitas
export async function exportarVisitasCSV() {
  const response = await api.get("/seguridad/export/visitas.csv", {
    responseType: "blob",
  });
  
  const blob = new Blob([response.data], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "visitas.csv";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
```

### 4.6 Mantenimiento
```typescript
export async function listarSolicitudesMantenimiento(params?: {
  categoria?: "PLOMERIA" | "ELECTRICIDAD" | "LIMPIEZA" | "JARDINERIA" | "PINTURA" | "OTRO";
  prioridad?: "BAJA" | "MEDIA" | "ALTA" | "URGENTE";
  estado?: "PENDIENTE" | "EN_PROGRESO" | "COMPLETADA" | "CANCELADA";
  solicitante?: number;
  asignado_a?: number;
  fecha_solicitud__gte?: string;
  fecha_solicitud__lte?: string;
  search?: string;
  ordering?: string;
}): Promise<SolicitudMantenimiento[]> {
  const { data } = await api.get("/mantenimiento/solicitudes/", { params });
  return data;
}

export async function crearSolicitudMantenimiento(solicitud: {
  titulo: string;
  descripcion: string;
  categoria: string;
  prioridad: string;
}): Promise<SolicitudMantenimiento> {
  const { data } = await api.post("/mantenimiento/solicitudes/", solicitud);
  return data;
}

export async function actualizarSolicitudMantenimiento(
  id: number,
  solicitud: Partial<SolicitudMantenimiento>
): Promise<SolicitudMantenimiento> {
  const { data } = await api.put(`/mantenimiento/solicitudes/${id}/`, solicitud);
  return data;
}
```

### 4.7 Notificaciones
```typescript
export async function registrarTokenDispositivo(token: {
  token: string;
  platform: "android" | "ios" | "web";
  active?: boolean;
}) {
  const { data } = await api.post("/notificaciones/token/", token);
  return data;
}

export async function enviarNotificacionDemo() {
  const { data } = await api.post("/notificaciones/demo/");
  return data;
}
```

### 4.8 Auditoría (Sistema Automático + Consulta)
```typescript
export type RegistroAuditoria = {
  id: number;
  timestamp: string; // ISO datetime
  timestamp_formatted: string; // Formato legible: "2025-10-01 20:45:30"
  usuario?: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
  };
  ip_address?: string;
  accion: string;
  descripcion?: string;
};

// Consulta de registros de auditoría (solo administradores)
export async function listarAuditoria(params?: {
  usuario?: number;
  accion__icontains?: string;
  timestamp__gte?: string;
  timestamp__lte?: string;
  ip_address?: string;
  search?: string;
  ordering?: string;
}): Promise<RegistroAuditoria[]> {
  const { data } = await api.get("/auditoria/bitacora/", { params });
  return data;
}

export async function getRegistroAuditoria(id: number): Promise<RegistroAuditoria> {
  const { data } = await api.get(`/auditoria/bitacora/${id}/`);
  return data;
}

// Funciones helper para consultas específicas
export async function getAuditoriaUsuario(userId: number, fechaInicio?: string, fechaFin?: string) {
  return await listarAuditoria({
    usuario: userId,
    timestamp__gte: fechaInicio,
    timestamp__lte: fechaFin,
    ordering: "-timestamp"
  });
}

export async function getAuditoriaPorAccion(accion: string, fechaInicio?: string, fechaFin?: string) {
  return await listarAuditoria({
    accion__icontains: accion,
    timestamp__gte: fechaInicio,
    timestamp__lte: fechaFin,
    ordering: "-timestamp"
  });
}

// Consulta eventos financieros específicos
export async function getAuditoriaFinanciera(fechaInicio?: string, fechaFin?: string) {
  return await listarAuditoria({
    accion__icontains: "Financiero",
    timestamp__gte: fechaInicio,
    timestamp__lte: fechaFin,
    ordering: "-timestamp"
  });
}

// Consulta eventos de seguridad
export async function getAuditoriaSeguridad(fechaInicio?: string, fechaFin?: string) {
  return await listarAuditoria({
    accion__icontains: "Seguridad",
    timestamp__gte: fechaInicio,
    timestamp__lte: fechaFin,
    ordering: "-timestamp"
  });
}
```

**🚨 SISTEMA AUTOMÁTICO DE AUDITORÍA Y NOTIFICACIONES:**

Tu backend tiene un **sistema completamente automático** que:

**📊 REGISTRA AUTOMÁTICAMENTE:**
- ✅ Todos los logins/logouts/intentos fallidos
- ✅ Creación de gastos y multas (con detalles completos)
- ✅ Registros de pagos y confirmaciones
- ✅ Registro de visitantes y eventos de seguridad
- ✅ Cambios de estado importantes en el sistema

**📱 NOTIFICA AUTOMÁTICAMENTE:**
- ✅ **Multa asignada** → Propietario + residentes de la propiedad afectada
- ✅ **Gasto asignado** → Usuarios relacionados con la propiedad
- ✅ **Pago recibido** → Confirmación a los usuarios que pagaron
- ✅ **Visitante registrado** → Alerta al propietario de la propiedad visitada
- ✅ **Eventos de seguridad** → Según tipo: propiedad específica o todos los usuarios

**🔄 FLUJO COMPLETAMENTE AUTOMÁTICO:**
```
1. Acción en el sistema (admin crea multa para Casa #12)
2. Se registra en auditoría automáticamente con detalles
3. Sistema identifica usuarios relacionados (propietario + residentes Casa #12)
4. Envía notificaciones push automáticamente: "💰 Nueva Multa: $50.00"
5. Todo queda trazado para auditorías futuras
```

**⚡ Para el Frontend:**
- **NO necesitas código extra** - Todo es automático
- Solo registra tokens de dispositivo para recibir notificaciones
- Consulta auditoría si necesitas ver el historial
- Los usuarios reciben notificaciones automáticamente
5. Todo queda trazado para consultas posteriores

No necesitas llamadas API adicionales desde el frontend - todo es automático.

---

## 5) Patrones de Filtrado Avanzado

### Operadores de filtro disponibles:
- `campo` - Coincidencia exacta
- `campo__icontains` - Contiene (insensible a mayúsculas)
- `campo__gte` - Mayor o igual que
- `campo__lte` - Menor o igual que
- `campo__gt` - Mayor que
- `campo__lt` - Menor que
- `campo__in` - Está en la lista
- `fecha__gte` / `fecha__lte` - Rangos de fechas

### Ejemplos de uso:
```typescript
// Búsqueda con múltiples filtros
const gastos = await listarGastos({
  anio: 2025,
  mes: 10,
  categoria: "EXPENSA",
  monto__gte: 100,
  monto__lte: 1000,
  fecha_emision__gte: "2025-01-01",
  pagado: false,
  ordering: "-fecha_emision"
});

// Búsqueda de texto libre
const visitantes = await listarVisitantes({
  search: "Juan",
  fecha_ingreso__gte: "2025-10-01",
  ordering: "-fecha_ingreso"
});
```

---

## 6) Manejo de Errores

```typescript
export function getApiError(error: unknown): string {
  const response = (error as any)?.response;
  if (!response) return "Error de conexión";
  
  const { status, data } = response;
  
  switch (status) {
    case 400:
      if (data?.detail) return data.detail;
      if (typeof data === "object") {
        return Object.entries(data)
          .map(([field, errors]) => `${field}: ${errors}`)
          .join(", ");
      }
      return "Datos inválidos";
    case 401:
      return "No autenticado";
    case 403:
      return "Sin permisos";
    case 404:
      return "Recurso no encontrado";
    case 500:
      return data?.error || "Error interno del servidor";
    default:
      return `Error HTTP ${status}`;
  }
}

// Ejemplo de uso
try {
  const result = await login({ username: "admin", password: "wrong" });
} catch (error) {
  const message = getApiError(error);
  console.error("Error de login:", message);
  // Mostrar mensaje al usuario
}
```

---

## 7) Componente React de Ejemplo

```tsx
import React, { useState, useEffect } from "react";
import { listarGastos, getApiError } from "./api";
import type { Gasto } from "./types";

export function ListaGastos() {
  const [gastos, setGastos] = useState<Gasto[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filtros, setFiltros] = useState({
    anio: new Date().getFullYear(),
    mes: new Date().getMonth() + 1,
    pagado: false,
  });

  useEffect(() => {
    cargarGastos();
  }, [filtros]);

  const cargarGastos = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await listarGastos({
        ...filtros,
        ordering: "-fecha_emision",
      });
      setGastos(data);
    } catch (err) {
      setError(getApiError(err));
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Cargando...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Gastos</h2>
      
      {/* Filtros */}
      <div className="filtros">
        <select
          value={filtros.anio}
          onChange={(e) => setFiltros({...filtros, anio: Number(e.target.value)})}
        >
          {[2023, 2024, 2025].map(year => (
            <option key={year} value={year}>{year}</option>
          ))}
        </select>
        
        <select
          value={filtros.mes}
          onChange={(e) => setFiltros({...filtros, mes: Number(e.target.value)})}
        >
          {Array.from({length: 12}, (_, i) => (
            <option key={i+1} value={i+1}>{i+1}</option>
          ))}
        </select>
        
        <label>
          <input
            type="checkbox"
            checked={!filtros.pagado}
            onChange={(e) => setFiltros({...filtros, pagado: !e.target.checked})}
          />
          Solo pendientes
        </label>
      </div>

      {/* Lista */}
      <div className="gastos-lista">
        {gastos.map(gasto => (
          <div key={gasto.id} className="gasto-item">
            <h3>{gasto.descripcion}</h3>
            <p>Monto: ${gasto.monto}</p>
            <p>Fecha: {gasto.fecha_emision}</p>
            <p>Estado: {gasto.pagado ? "Pagado" : "Pendiente"}</p>
            <p>Categoría: {gasto.categoria}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 8) Endpoints de Archivos y Descargas

### PDFs y CSVs
```typescript
// Descargar comprobante de pago (PDF)
export async function descargarComprobante(pagoId: number) {
  const response = await api.get(`/finanzas/pagos/${pagoId}/comprobante/`, {
    responseType: "blob",
  });
  
  downloadFile(response.data, `comprobante_${pagoId}.pdf`, "application/pdf");
}

// Exportar visitas (CSV)
export async function exportarVisitas() {
  const response = await api.get("/seguridad/export/visitas.csv", {
    responseType: "blob",
  });
  
  downloadFile(response.data, "visitas.csv", "text/csv");
}

// Función helper para descargas
function downloadFile(blob: Blob, filename: string, mimeType: string) {
  const file = new Blob([blob], { type: mimeType });
  const url = URL.createObjectURL(file);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
```

---

## 9) Configuración CORS y Deployment

### Variables de Entorno (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Para producción:
```typescript
const config = {
  apiUrl: import.meta.env.VITE_API_URL || "https://api.tudominio.com",
  stripeKey: import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY,
  isDevelopment: import.meta.env.MODE === "development",
};
```

---

## 10) Resumen de Endpoints Principales

| Área | Método | Endpoint | Descripción |
|------|--------|----------|-------------|
| **Auth** | POST | `/api/usuarios/login/` | Login con token |
| **Auth** | POST | `/api/usuarios/registro/` | Registro de usuario |
| **Perfil** | GET | `/api/usuarios/perfil/` | Datos del usuario actual |
| **IA** | POST | `/api/usuarios/reconocimiento/registrar-rostro/` | Registrar rostro |
| **IA** | POST | `/api/seguridad/ia/verificar-rostro/` | Verificar rostro |
| **Finanzas** | GET | `/api/finanzas/estado-cuenta-unificado/` | Estado de cuenta |
| **Finanzas** | GET | `/api/finanzas/gastos/` | Lista de gastos |
| **Finanzas** | GET | `/api/finanzas/multas/` | Lista de multas |
| **Finanzas** | GET | `/api/finanzas/reservas/` | Lista de reservas |
| **Pagos** | POST | `/api/finanzas/pagos/crear-checkout-stripe/` | Crear sesión Stripe |
| **Pagos** | GET | `/api/finanzas/pagos/{id}/comprobante/` | Descargar PDF |
| **Condominio** | GET | `/api/condominio/areas-comunes/` | Áreas comunes |
| **Condominio** | GET | `/api/condominio/reglas/` | Reglas |
| **Seguridad** | POST | `/api/seguridad/control-acceso-vehicular/` | Control vehicular |
| **Seguridad** | GET | `/api/seguridad/visitantes/` | Lista visitantes |
| **Seguridad** | GET | `/api/seguridad/export/visitas.csv` | Export CSV |
| **Mantenimiento** | GET | `/api/mantenimiento/solicitudes/` | Solicitudes |
| **Notificaciones** | POST | `/api/notificaciones/token/` | Registrar device token |
| **Auditoría** | GET | `/api/auditoria/bitacora/` | Consultar registros de auditoría ✅ |

---

**¡Esta guía está 100% actualizada con el sistema completo!** Todos los endpoints, parámetros y tipos están verificados contra el schema generado de tu backend.

## 🚀 Sistema Completo de Auditoría y Notificaciones

### **Configuración de Notificaciones Push**
```typescript
// 1. Registrar token de dispositivo al hacer login
export async function setupNotifications(userId: number) {
  try {
    // Obtener token de FCM (Firebase Cloud Messaging)
    const messaging = getMessaging();
    const token = await getToken(messaging, { 
      vapidKey: "tu-vapid-key" 
    });
    
    // Registrar en el backend
    await registrarTokenDispositivo({
      token: token,
      platform: "web", // "android", "ios", "web"
      active: true
    });
    
    console.log("✅ Notificaciones configuradas correctamente");
  } catch (error) {
    console.error("❌ Error configurando notificaciones:", error);
  }
}

// 2. Manejar notificaciones recibidas
onMessage(messaging, (payload) => {
  console.log('📱 Notificación recibida:', payload);
  
  // Mostrar notificación en el UI
  showNotification({
    title: payload.notification?.title || "Nueva notificación",
    body: payload.notification?.body || "",
    data: payload.data
  });
});
```

### **Eventos que Generan Notificaciones Automáticamente**
```typescript
// Cuando el admin hace estas acciones, las notificaciones se envían automáticamente:

// 1. Crear gasto → notifica a propietario + residentes
await api.post("/finanzas/gastos/", {
  propiedad: 12,
  monto: "150.00",
  descripcion: "Expensa mensual octubre"
});
// 📱 Auto-notifica: "💰 Nuevo Gasto: $150.00 - Expensa mensual octubre"

// 2. Crear multa → notifica a propietario + residentes  
await api.post("/finanzas/multas/", {
  propiedad: 12,
  monto: "50.00",
  concepto: "Ruido excesivo"
});
// 📱 Auto-notifica: "💰 Nueva Multa: $50.00 - Ruido excesivo"

// 3. Registrar visitante → notifica al propietario de la propiedad
await api.post("/seguridad/visitantes/", {
  nombre_completo: "Juan Pérez",
  documento: "12345678",
  propiedad_visitada: 12,
  motivo_visita: "Visita familiar"
});
// 📱 Auto-notifica: "👤 Visitante Registrado - Juan Pérez"

// 4. Registrar pago → confirma al usuario
await api.post("/finanzas/multas/1/registrar_pago/", {
  monto_pagado: "50.00"
});
// 📱 Auto-notifica: "✅ Pago Recibido - $50.00 ¡Gracias!"
```

### **Dashboard de Auditoría (Solo Admins)**
```typescript
// Componente para mostrar actividad reciente
export function DashboardAuditoria() {
  const [actividad, setActividad] = useState<RegistroAuditoria[]>([]);
  
  useEffect(() => {
    cargarActividadReciente();
  }, []);
  
  const cargarActividadReciente = async () => {
    try {
      // Últimas 24 horas
      const hace24h = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
      const registros = await listarAuditoria({
        timestamp__gte: hace24h,
        ordering: "-timestamp"
      });
      setActividad(registros.slice(0, 10)); // Últimos 10
    } catch (error) {
      console.error("Error cargando auditoría:", error);
    }
  };
  
  return (
    <div className="dashboard-auditoria">
      <h3>📊 Actividad Reciente (24h)</h3>
      {actividad.map(registro => (
        <div key={registro.id} className="registro-item">
          <div className="timestamp">{registro.timestamp_formatted}</div>
          <div className="usuario">{registro.usuario?.username || "Sistema"}</div>
          <div className="accion">{registro.accion}</div>
          <div className="ip">{registro.ip_address}</div>
        </div>
      ))}
    </div>
  );
}
```

Para usar esta guía:
1. Copia las funciones que necesites
2. Ajusta las URLs base según tu entorno  
3. Configura Firebase Cloud Messaging para notificaciones push
4. Implementa los componentes UI según tus necesidades
5. Los tipos TypeScript están listos para usar

**🎯 Tu sistema es completamente automático**: cada evento importante se registra y notifica automáticamente a los usuarios correctos sin intervención manual. ¡Perfecto para un condominio moderno!