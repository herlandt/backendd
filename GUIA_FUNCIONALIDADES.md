# GUÍA COMPLETA DE FUNCIONALIDADES - BACKEND CONDOMINIO

## ESTRUCTURA DE RUTAS Y FUNCIONALIDADES

### 1. AUTENTICACIÓN Y USUARIOS 👤

#### Rutas Base de Autenticación:
- **POST** `/api/login/` → `obtain_auth_token` ➤ **Iniciar sesión**
- **POST** `/api/registro/` → `RegistroView.as_view()` ➤ **Registrar usuario**
- **POST** `/api/dispositivos/registrar/` → `RegistrarDispositivoView.as_view()` ➤ **Registrar dispositivo móvil**

#### Rutas de Usuarios (/api/usuarios/):
- **GET** `/api/usuarios/residentes/` → `ResidenteViewSet.list()` ➤ **Listar residentes** 🔒 Admin
- **POST** `/api/usuarios/residentes/` → `ResidenteViewSet.create()` ➤ **Crear residente** 🔒 Admin
- **GET** `/api/usuarios/residentes/{id}/` → `ResidenteViewSet.retrieve()` ➤ **Ver residente** 🔒 Admin
- **PUT** `/api/usuarios/residentes/{id}/` → `ResidenteViewSet.update()` ➤ **Actualizar residente** 🔒 Admin
- **DELETE** `/api/usuarios/residentes/{id}/` → `ResidenteViewSet.destroy()` ➤ **Eliminar residente** 🔒 Admin

- **POST** `/api/usuarios/login/` → `LoginView.as_view()` ➤ **Login alternativo**
- **POST** `/api/usuarios/registro/` → `RegistroView.as_view()` ➤ **Registro alternativo**
- **POST** `/api/usuarios/dispositivos/registrar/` → `RegistrarDispositivoView.as_view()` ➤ **Registrar dispositivo**
- **POST** `/api/usuarios/reconocimiento/registrar-rostro/` → `RegistrarRostroView.as_view()` ➤ **Registrar rostro facial** 🔒 Usuario
- **GET** `/api/usuarios/perfil/` → `PerfilUsuarioView.as_view()` ➤ **Ver perfil usuario** 🔒 Usuario
- **POST** `/api/usuarios/setup/crear-primer-admin/` → `CrearAdminView.as_view()` ➤ **Crear primer admin**

### 2. SEGURIDAD 🔐

#### Rutas de Control Vehicular:
- **POST** `/api/seguridad/control-acceso-vehicular/` → `ControlAccesoVehicularView.post()` ➤ **Controlar acceso vehículos** 🔒 Usuario
- **POST** `/api/seguridad/control-salida-vehicular/` → `ControlSalidaVehicularView.post()` ➤ **Registrar salida vehículos** 🔒 Usuario

#### Rutas CRUD Seguridad:
- **GET** `/api/seguridad/visitas/` → `VisitaViewSet.list()` ➤ **Listar visitas** 🔒 Usuario
- **POST** `/api/seguridad/visitas/` → `VisitaViewSet.create()` ➤ **Crear visita** 🔒 Usuario
- **GET** `/api/seguridad/visitas/{id}/` → `VisitaViewSet.retrieve()` ➤ **Ver visita** 🔒 Usuario
- **PUT** `/api/seguridad/visitas/{id}/` → `VisitaViewSet.update()` ➤ **Actualizar visita** 🔒 Usuario
- **DELETE** `/api/seguridad/visitas/{id}/` → `VisitaViewSet.destroy()` ➤ **Eliminar visita** 🔒 Usuario

- **GET** `/api/seguridad/vehiculos/` → `VehiculoViewSet.list()` ➤ **Listar vehículos** 🔒 Usuario
- **POST** `/api/seguridad/vehiculos/` → `VehiculoViewSet.create()` ➤ **Registrar vehículo** 🔒 Usuario
- **PUT** `/api/seguridad/vehiculos/{id}/` → `VehiculoViewSet.update()` ➤ **Actualizar vehículo** 🔒 Usuario
- **DELETE** `/api/seguridad/vehiculos/{id}/` → `VehiculoViewSet.destroy()` ➤ **Eliminar vehículo** 🔒 Usuario

- **GET** `/api/seguridad/visitantes/` → `VisitanteViewSet.list()` ➤ **Listar visitantes** 🔒 Usuario
- **POST** `/api/seguridad/visitantes/` → `VisitanteViewSet.create()` ➤ **Registrar visitante** 🔒 Usuario
- **PUT** `/api/seguridad/visitantes/{id}/` → `VisitanteViewSet.update()` ➤ **Actualizar visitante** 🔒 Usuario
- **DELETE** `/api/seguridad/visitantes/{id}/` → `VisitanteViewSet.destroy()` ➤ **Eliminar visitante** 🔒 Usuario

- **GET** `/api/seguridad/eventos/` → `EventoSeguridadViewSet.list()` ➤ **Listar eventos seguridad** 🔒 Usuario
- **POST** `/api/seguridad/eventos/` → `EventoSeguridadViewSet.create()` ➤ **Crear evento seguridad** 🔒 Usuario

#### Rutas Especiales Seguridad:
- **GET** `/api/seguridad/visitas-abiertas/` → `VisitasAbiertasView.get()` ➤ **Ver visitas abiertas** 🔒 Admin
- **GET** `/api/seguridad/export/visitas.csv` → `ExportVisitasCSVView.get()` ➤ **Exportar visitas CSV** 🔒 Admin
- **POST** `/api/seguridad/cerrar-visitas-vencidas/` → `CerrarVisitasVencidasView.post()` ➤ **Cerrar visitas vencidas** 🔒 Admin

#### Rutas Dashboard:
- **GET** `/api/seguridad/dashboard/resumen/` → `DashboardResumenView.get()` ➤ **Dashboard resumen** 🔒 Usuario
- **GET** `/api/seguridad/dashboard/series/` → `DashboardSeriesView.get()` ➤ **Dashboard series** 🔒 Usuario
- **GET** `/api/seguridad/dashboard/top-visitantes/` → `DashboardTopVisitantesView.get()` ➤ **Top visitantes** 🔒 Usuario

#### Rutas IA:
- **POST** `/api/seguridad/ia/control-vehicular/` → `IAControlVehicularView.post()` ➤ **Control vehicular IA** 🔑 API-Key
- **POST** `/api/seguridad/ia/verificar-rostro/` → `VerificarRostroView.post()` ➤ **Verificar rostro IA** 🔑 API-Key
- **GET** `/api/seguridad/detecciones/` → `DeteccionListView.get()` ➤ **Listar detecciones IA** 🔒 Usuario

### 3. FINANZAS 💰

#### Rutas CRUD Gastos:
- **GET** `/api/finanzas/gastos/` → `GastoViewSet.list()` ➤ **Listar gastos** 🔒 Usuario
- **POST** `/api/finanzas/gastos/` → `GastoViewSet.create()` ➤ **Crear gasto** 🔒 Usuario
- **GET** `/api/finanzas/gastos/{id}/` → `GastoViewSet.retrieve()` ➤ **Ver gasto** 🔒 Usuario
- **PUT** `/api/finanzas/gastos/{id}/` → `GastoViewSet.update()` ➤ **Actualizar gasto** 🔒 Usuario
- **DELETE** `/api/finanzas/gastos/{id}/` → `GastoViewSet.destroy()` ➤ **Eliminar gasto** 🔒 Usuario

#### Rutas Especiales Gastos:
- **POST** `/api/finanzas/gastos/crear_mensual/` → `GastoViewSet.crear_mensual()` ➤ **Crear gastos mensuales** 🔒 Admin
- **POST** `/api/finanzas/gastos/{id}/registrar_pago/` → `GastoViewSet.registrar_pago()` ➤ **Pagar gasto individual** 🔒 Usuario
- **POST** `/api/finanzas/gastos/pagar_en_lote/` → `GastoViewSet.pagar_en_lote()` ➤ **Pagar múltiples gastos** 🔒 Usuario

#### Rutas CRUD Multas:
- **GET** `/api/finanzas/multas/` → `MultaViewSet.list()` ➤ **Listar multas** 🔒 Usuario
- **POST** `/api/finanzas/multas/` → `MultaViewSet.create()` ➤ **Crear multa** 🔒 Usuario
- **POST** `/api/finanzas/multas/{id}/registrar_pago/` → `MultaViewSet.registrar_pago()` ➤ **Pagar multa individual** 🔒 Usuario
- **POST** `/api/finanzas/multas/pagar_en_lote/` → `MultaViewSet.pagar_en_lote()` ➤ **Pagar múltiples multas** 🔒 Usuario

#### Rutas CRUD Pagos:
- **GET** `/api/finanzas/pagos/` → `PagoViewSet.list()` ➤ **Listar pagos** 🔒 Usuario
- **POST** `/api/finanzas/pagos/` → `PagoViewSet.create()` ➤ **Crear pago** 🔒 Usuario
- **GET** `/api/finanzas/pagos-multas/` → `PagoMultaViewSet.list()` ➤ **Listar pagos multas** 🔒 Usuario

#### Rutas CRUD Reservas:
- **GET** `/api/finanzas/reservas/` → `ReservaViewSet.list()` ➤ **Listar reservas** 🔒 Usuario
- **POST** `/api/finanzas/reservas/` → `ReservaViewSet.create()` ➤ **Crear reserva** 🔒 Usuario
- **PUT** `/api/finanzas/reservas/{id}/` → `ReservaViewSet.update()` ➤ **Actualizar reserva** 🔒 Usuario
- **DELETE** `/api/finanzas/reservas/{id}/` → `ReservaViewSet.destroy()` ➤ **Eliminar reserva** 🔒 Usuario

#### Rutas CRUD Egresos/Ingresos:
- **GET** `/api/finanzas/egresos/` → `EgresoViewSet.list()` ➤ **Listar egresos** 🔒 Usuario
- **POST** `/api/finanzas/egresos/` → `EgresoViewSet.create()` ➤ **Crear egreso** 🔒 Usuario
- **GET** `/api/finanzas/ingresos/` → `IngresoViewSet.list()` ➤ **Listar ingresos** 🔒 Usuario
- **POST** `/api/finanzas/ingresos/` → `IngresoViewSet.create()` ➤ **Crear ingreso** 🔒 Usuario

#### Rutas Comprobantes:
- **GET** `/api/finanzas/pagos/{id}/comprobante/` → `ReciboPagoPDFView.get()` ➤ **Comprobante pago PDF** 🔒 Público
- **GET** `/api/finanzas/pagos-multas/{id}/comprobante/` → `ReciboPagoMultaPDFView.get()` ➤ **Comprobante multa PDF** 🔒 Público

#### Rutas Reportes:
- **GET** `/api/finanzas/reportes/estado-morosidad/` → `ReporteMorosidadView.get()` ➤ **Reporte morosidad** 🔒 Admin
- **GET** `/api/finanzas/reportes/resumen/` → `ReporteResumenView.get()` ➤ **Reporte resumen** 🔒 Usuario
- **GET** `/api/finanzas/reportes/financiero/` → `ReporteFinancieroView.get()` ➤ **Reporte financiero** 🔒 Usuario
- **GET** `/api/finanzas/reportes/uso-areas-comunes/` → `ReporteUsoAreasComunesView.get()` ➤ **Reporte uso áreas** 🔒 Usuario

#### Rutas Pagos Online:
- **POST** `/api/finanzas/pagos/{id}/simular/` → `SimularPagoView.post()` ➤ **Simular pago QR** 🔒 Usuario
- **POST** `/api/finanzas/webhook/pagosnet/` → `WebhookConfirmacionPagoView.post()` ➤ **Webhook PagosNet** 🔒 Público
- **POST** `/api/finanzas/reservas/{id}/pagar/` → `PagarReservaView.post()` ➤ **Pagar reserva QR** 🔒 Usuario

#### Rutas Utilidades:
- **POST** `/api/finanzas/expensas/generar/` → `GenerarExpensasView.post()` ➤ **Generar expensas** 🔒 Admin
- **GET** `/api/finanzas/estado-de-cuenta/` → `EstadoDeCuentaView.get()` ➤ **Estado de cuenta** 🔒 Usuario

### 4. CONDOMINIO 🏢

#### Rutas CRUD Propiedades:
- **GET** `/api/condominio/propiedades/` → `PropiedadViewSet.list()` ➤ **Listar propiedades** 🔒 Usuario
- **POST** `/api/condominio/propiedades/` → `PropiedadViewSet.create()` ➤ **Crear propiedad** 🔒 Usuario
- **GET** `/api/condominio/propiedades/{id}/` → `PropiedadViewSet.retrieve()` ➤ **Ver propiedad** 🔒 Usuario
- **PUT** `/api/condominio/propiedades/{id}/` → `PropiedadViewSet.update()` ➤ **Actualizar propiedad** 🔒 Usuario
- **DELETE** `/api/condominio/propiedades/{id}/` → `PropiedadViewSet.destroy()` ➤ **Eliminar propiedad** 🔒 Usuario

#### Rutas CRUD Áreas Comunes:
- **GET** `/api/condominio/areas-comunes/` → `AreaComunViewSet.list()` ➤ **Listar áreas comunes** 🔒 Usuario
- **GET** `/api/condominio/areas-comunes/{id}/` → `AreaComunViewSet.retrieve()` ➤ **Ver área común** 🔒 Usuario

#### Rutas CRUD Avisos:
- **GET** `/api/condominio/avisos/` → `AvisoViewSet.list()` ➤ **Listar avisos** 🔒 Usuario
- **POST** `/api/condominio/avisos/` → `AvisoViewSet.create()` ➤ **Crear aviso** 🔒 Usuario
- **GET** `/api/condominio/avisos/{id}/` → `AvisoViewSet.retrieve()` ➤ **Ver aviso** 🔒 Usuario
- **PUT** `/api/condominio/avisos/{id}/` → `AvisoViewSet.update()` ➤ **Actualizar aviso** 🔒 Usuario
- **DELETE** `/api/condominio/avisos/{id}/` → `AvisoViewSet.destroy()` ➤ **Eliminar aviso** 🔒 Usuario

#### Rutas CRUD Reglas:
- **GET** `/api/condominio/reglas/` → `ReglaViewSet.list()` ➤ **Listar reglas** 🔒 Usuario
- **GET** `/api/condominio/reglas/{id}/` → `ReglaViewSet.retrieve()` ➤ **Ver regla** 🔒 Usuario

### 5. MANTENIMIENTO 🔧

#### Rutas CRUD Personal:
- **GET** `/api/mantenimiento/personal/` → `PersonalMantenimientoViewSet.list()` ➤ **Listar personal** 🔒 Usuario
- **POST** `/api/mantenimiento/personal/` → `PersonalMantenimientoViewSet.create()` ➤ **Crear personal** 🔒 Staff
- **GET** `/api/mantenimiento/personal/{id}/` → `PersonalMantenimientoViewSet.retrieve()` ➤ **Ver personal** 🔒 Usuario
- **PUT** `/api/mantenimiento/personal/{id}/` → `PersonalMantenimientoViewSet.update()` ➤ **Actualizar personal** 🔒 Staff
- **DELETE** `/api/mantenimiento/personal/{id}/` → `PersonalMantenimientoViewSet.destroy()` ➤ **Eliminar personal** 🔒 Staff

#### Rutas CRUD Solicitudes:
- **GET** `/api/mantenimiento/solicitudes/` → `SolicitudMantenimientoViewSet.list()` ➤ **Listar solicitudes** 🔒 Usuario
- **POST** `/api/mantenimiento/solicitudes/` → `SolicitudMantenimientoViewSet.create()` ➤ **Crear solicitud** 🔒 Usuario (sin deudas)
- **GET** `/api/mantenimiento/solicitudes/{id}/` → `SolicitudMantenimientoViewSet.retrieve()` ➤ **Ver solicitud** 🔒 Usuario
- **PUT** `/api/mantenimiento/solicitudes/{id}/` → `SolicitudMantenimientoViewSet.update()` ➤ **Actualizar solicitud** 🔒 Usuario
- **DELETE** `/api/mantenimiento/solicitudes/{id}/` → `SolicitudMantenimientoViewSet.destroy()` ➤ **Eliminar solicitud** 🔒 Usuario

#### Rutas Especiales Mantenimiento:
- **POST** `/api/mantenimiento/solicitudes/{id}/cambiar_estado/` → `SolicitudMantenimientoViewSet.cambiar_estado()` ➤ **Cambiar estado solicitud** 🔒 Usuario
- **POST** `/api/mantenimiento/solicitudes/{id}/asignar/` → `SolicitudMantenimientoViewSet.asignar()` ➤ **Asignar personal** 🔒 Usuario

### 6. NOTIFICACIONES 📱

#### Rutas Notificaciones:
- **POST** `/api/notificaciones/token/` → `RegistrarDeviceTokenView.post()` ➤ **Registrar token FCM** 🔒 Usuario
- **POST** `/api/notificaciones/demo/` → `EnviarNotificacionDemoView.post()` ➤ **Enviar notificación demo** 🔒 Admin
- **POST** `/api/notificaciones/registrar-dispositivo/` → `RegistrarDispositivoView.post()` ➤ **Registrar dispositivo** 🔒 Usuario

### 7. DOCUMENTACIÓN 📚

#### Rutas de Documentación:
- **GET** `/api/schema/` → `SpectacularAPIView.as_view()` ➤ **Esquema OpenAPI** 🔒 Público
- **GET** `/api/schema/swagger-ui/` → `SpectacularSwaggerView.as_view()` ➤ **Documentación Swagger** 🔒 Público
- **GET** `/api/schema/redoc/` → `SpectacularRedocView.as_view()` ➤ **Documentación ReDoc** 🔒 Público
- **GET** `/api/docs/` → `SpectacularSwaggerView.as_view()` ➤ **Documentación alternativa** 🔒 Público
- **GET** `/api/redoc/` → `SpectacularRedocView.as_view()` ➤ **ReDoc alternativo** 🔒 Público

### 8. ADMINISTRACIÓN 👑

#### Panel de Administración:
- **GET** `/admin/` → `admin.site.urls` ➤ **Panel de administración Django** 🔒 Admin

---

## LEYENDA DE PERMISOS

🔒 **Usuario** - Requiere autenticación (Token)  
🔒 **Admin** - Requiere permisos de administrador  
🔒 **Staff** - Requiere permisos de staff  
🔑 **API-Key** - Requiere clave API específica  
🔒 **Público** - Acceso público (sin autenticación)  
🔒 **Usuario (sin deudas)** - Usuario autenticado sin deudas pendientes

---

## PATRONES DE URL

### ViewSet Routes (CRUD completo):
- `GET /api/app/modelo/` → **list()** - Listar todos
- `POST /api/app/modelo/` → **create()** - Crear nuevo
- `GET /api/app/modelo/{id}/` → **retrieve()** - Ver específico
- `PUT /api/app/modelo/{id}/` → **update()** - Actualizar completo
- `PATCH /api/app/modelo/{id}/` → **partial_update()** - Actualizar parcial
- `DELETE /api/app/modelo/{id}/` → **destroy()** - Eliminar

### Custom Actions:
- `POST /api/app/modelo/{id}/accion/` → **accion()** - Acción personalizada
- `POST /api/app/modelo/accion_global/` → **accion_global()** - Acción sin ID

---

Esta guía proporciona una vista completa de todas las funcionalidades disponibles en el backend, organizadas por módulos funcionales y con claridad sobre qué hace cada endpoint y qué permisos requiere.