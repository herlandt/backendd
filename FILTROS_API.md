# Filtros Avanzados de la API

Este documento describe los filtros avanzados implementados en la API del sistema de condominio.

## Configuración

Los filtros están implementados usando `django-filter` con los siguientes backends configurados:

- **DjangoFilterBackend**: Filtros por campos específicos
- **SearchFilter**: Búsqueda de texto
- **OrderingFilter**: Ordenamiento de resultados

## Tipos de Filtros Disponibles

### Filtros por Campo Exacto
- `field=value` - Coincidencia exacta

### Filtros de Rango
- `field__gte=value` - Mayor o igual que
- `field__lte=value` - Menor o igual que

### Filtros de Texto
- `field__icontains=text` - Contiene texto (insensible a mayúsculas)

### Filtros Booleanos
- `field=true/false` - Valores booleanos
- `field__isnull=true/false` - Valores nulos o no nulos

## Módulos con Filtros Implementados

### 1. Finanzas (`/api/finanzas/`)

#### GastoViewSet (`/gastos/`)
```
# Filtros de campo
?mes=9&ano=2025&pagado=false&monto__gte=100&monto__lte=500

# Búsqueda de texto
?search=agua

# Ordenamiento
?ordering=-fecha_vencimiento
```

**Campos disponibles:**
- `mes`: [exact]
- `ano`: [exact] 
- `categoria`: [exact, icontains]
- `monto`: [gte, lte]
- `pagado`: [exact]
- `fecha_vencimiento`: [gte, lte, exact]

#### MultaViewSet (`/multas/`)
```
# Filtros
?usuario=1&pagada=false&monto__gte=50

# Búsqueda
?search=estacionamiento

# Ordenamiento
?ordering=-fecha_multa
```

**Campos disponibles:**
- `usuario`: [exact]
- `pagada`: [exact]
- `monto`: [gte, lte]
- `fecha_multa`: [gte, lte, exact]

#### ReservaViewSet (`/reservas/`)
```
# Filtros
?area_comun=1&fecha_reserva__gte=2025-01-01&pagada=true

# Búsqueda
?search=piscina
```

**Campos disponibles:**
- `area_comun`: [exact]
- `usuario`: [exact]
- `fecha_reserva`: [gte, lte, exact]
- `pagada`: [exact]
- `costo_total`: [gte, lte]

#### PagoViewSet (`/pagos/`)
```
# Filtros
?usuario=1&fecha_pago__gte=2025-01-01&metodo_pago=EFECTIVO

# Búsqueda
?search=transferencia
```

**Campos disponibles:**
- `usuario`: [exact]
- `monto`: [gte, lte]
- `fecha_pago`: [gte, lte, exact]
- `metodo_pago`: [exact]
- `gasto`: [exact]
- `multa`: [exact]
- `reserva`: [exact]

### 2. Seguridad (`/api/seguridad/`)

#### VisitaViewSet (`/visitas/`)
```
# Filtros
?propiedad=1&ingreso_real__isnull=true&fecha_ingreso_programado__gte=2025-01-01

# Búsqueda
?search=juan
```

**Campos disponibles:**
- `propiedad`: [exact]
- `visitante`: [exact]
- `fecha_ingreso_programado`: [gte, lte, exact]
- `fecha_salida_programada`: [gte, lte, exact]
- `ingreso_real`: [isnull]
- `salida_real`: [isnull]
- `estado`: [exact]

#### VehiculoViewSet (`/vehiculos/`)
```
# Filtros
?placa__icontains=ABC&tipo=AUTO&propiedad=1

# Búsqueda
?search=toyota
```

**Campos disponibles:**
- `placa`: [exact, icontains]
- `modelo`: [icontains]
- `color`: [exact, icontains]
- `propiedad`: [exact]
- `tipo`: [exact]

#### VisitanteViewSet (`/visitantes/`)
```
# Filtros
?cedula=123456789&nombre__icontains=maria

# Búsqueda
?search=garcia
```

**Campos disponibles:**
- `nombre`: [icontains]
- `cedula`: [exact]
- `telefono`: [exact, icontains]

#### EventoSeguridadViewSet (`/eventos/`)
```
# Filtros
?tipo=INCIDENTE&gravedad=ALTA&resuelto=false&fecha_hora__gte=2025-01-01

# Búsqueda
?search=ruido
```

**Campos disponibles:**
- `tipo`: [exact]
- `fecha_hora`: [gte, lte, exact]
- `ubicacion`: [icontains]
- `gravedad`: [exact]
- `resuelto`: [exact]

### 3. Mantenimiento (`/api/mantenimiento/`)

#### PersonalMantenimientoViewSet (`/personal/`)
```
# Filtros
?activo=true&especialidad__icontains=electricista

# Búsqueda
?search=carlos
```

**Campos disponibles:**
- `activo`: [exact]
- `especialidad`: [exact, icontains]
- `nombre`: [icontains]

#### SolicitudMantenimientoViewSet (`/solicitudes/`)
```
# Filtros
?estado=PENDIENTE&prioridad=ALTA&fecha_creacion__gte=2025-01-01&fecha_resolucion__isnull=true

# Búsqueda
?search=plomeria
```

**Campos disponibles:**
- `estado`: [exact]
- `propiedad`: [exact]
- `asignado_a`: [exact]
- `solicitado_por`: [exact]
- `fecha_creacion`: [gte, lte, exact]
- `fecha_resolucion`: [gte, lte, exact, isnull]
- `prioridad`: [exact]

### 4. Condominio (`/api/condominio/`)

#### PropiedadViewSet (`/propiedades/`)
```
# Filtros
?numero_casa__icontains=101&metros_cuadrados__gte=80&propietario=1

# Búsqueda
?search=101
```

**Campos disponibles:**
- `numero_casa`: [exact, icontains]
- `metros_cuadrados`: [gte, lte]
- `propietario`: [exact]

#### AreaComunViewSet (`/areas-comunes/`)
```
# Filtros
?nombre__icontains=piscina&capacidad__gte=10&costo_reserva__lte=50

# Búsqueda
?search=piscina
```

**Campos disponibles:**
- `nombre`: [icontains]
- `capacidad`: [gte, lte, exact]
- `costo_reserva`: [gte, lte, exact]

#### AvisoViewSet (`/avisos/`)
```
# Filtros
?titulo__icontains=reunion&fecha_publicacion__gte=2025-01-01

# Búsqueda
?search=reunion
```

**Campos disponibles:**
- `titulo`: [icontains]
- `fecha_publicacion`: [gte, lte, exact]

#### ReglaViewSet (`/reglas/`)
```
# Filtros
?categoria=SEGURIDAD&activa=true&codigo__icontains=RESTRICCION

# Búsqueda
?search=mascotas
```

**Campos disponibles:**
- `categoria`: [exact]
- `activa`: [exact]
- `codigo`: [exact, icontains]

### 5. Usuarios (`/api/usuarios/`)

#### ResidenteViewSet (`/residentes/`)
```
# Filtros
?propiedad=1&usuario__username__icontains=juan&usuario__email__icontains=gmail

# Búsqueda
?search=maria
```

**Campos disponibles:**
- `propiedad`: [exact]
- `usuario`: [exact]
- `usuario__username`: [icontains]
- `usuario__email`: [icontains]
- `usuario__first_name`: [icontains]
- `usuario__last_name`: [icontains]

## Ejemplos de Uso Combinado

### 1. Buscar gastos pendientes de servicios básicos en diciembre 2024
```
/api/finanzas/gastos/?mes=12&ano=2024&pagado=false&categoria__icontains=agua&ordering=-monto
```

### 2. Encontrar visitas programadas para hoy que no han ingresado
```
/api/seguridad/visitas/?fecha_ingreso_programado=2025-01-09&ingreso_real__isnull=true&ordering=fecha_ingreso_programado
```

### 3. Solicitudes de mantenimiento urgentes sin resolver
```
/api/mantenimiento/solicitudes/?prioridad=ALTA&estado=PENDIENTE&fecha_resolucion__isnull=true&ordering=-fecha_creacion
```

### 4. Propiedades grandes disponibles
```
/api/condominio/propiedades/?metros_cuadrados__gte=100&ordering=-metros_cuadrados
```

## Funcionalidades Adicionales

### Paginación
Todos los endpoints soportan paginación automática:
```
?page=2&page_size=20
```

### Búsqueda Global
Usar el parámetro `search` para buscar en múltiples campos de texto:
```
?search=maria garcia
```

### Ordenamiento Múltiple
```
?ordering=-fecha_creacion,nombre
```

## Optimización de Performance

Los campos más consultados tienen índices de base de datos para mejorar el rendimiento:
- Fechas (fecha_creacion, fecha_vencimiento, etc.)
- IDs de relaciones (usuario, propiedad, etc.)
- Campos de estado (pagado, activo, resuelto, etc.)
- Campos de texto frecuentemente buscados

## Notas de Seguridad

- Los filtros respetan los permisos de usuario implementados
- Los residentes solo ven datos relacionados con sus propiedades
- El personal de seguridad y mantenimiento ve datos según su rol
- Los propietarios tienen acceso completo a la información del condominio