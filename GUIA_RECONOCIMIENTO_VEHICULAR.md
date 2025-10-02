# 🚗 GUÍA COMPLETA: SISTEMA DE RECONOCIMIENTO VEHICULAR CON GATE

## 🎯 INTRODUCCIÓN

Este sistema implementa reconocimiento vehicular automático usando el video `test_video.mp4` como fuente de datos. Simula una cámara de gate que detecta matrículas y controla el acceso al condominio.

---

## 🏁 CONFIGURACIÓN INICIAL (PASO A PASO)

### PASO 1: 🗄️ Preparar Base de Datos

```bash
# 1. Ejecutar desde el directorio del proyecto
cd C:\Users\asus\Documents\desplegable\backendd

# 2. Crear vehículos de prueba
python setup_vehiculos.py
```

**Salida esperada:**
```
🚗 CREANDO VEHÍCULOS DE PRUEBA
==================================================
🧹 Limpiando vehículos existentes...
   🗑️  Eliminados X vehículos

🚗 Creando vehículos de prueba...
   ✅ ABC123 -> Casa 101 (Toyota Corolla - Casa 101)
   ✅ DEF456 -> Casa 102 (Honda Civic - Casa 102)
   ✅ XYZ789 -> Casa 103 (Chevrolet Spark - Casa 103)
   ✅ LMN012 -> Casa 104 (Nissan Sentra - Casa 104)
   ✅ GHI345 -> Sin asignar (Ford Focus - Visitante)
   ✅ JKL678 -> Sin asignar (Mazda 3 - Administración)
```

### PASO 2: 🖥️ Iniciar Backend

```bash
# En una terminal, asegúrate de que el servidor Django esté corriendo
python manage.py runserver
```

**Verifica que esté activo:** http://127.0.0.1:8000/api/

### PASO 3: 🎥 Ejecutar Simulador

**Opción 1: Interfaz Web (Recomendado)**
```bash
# En otra terminal
cd ia_scripts
python gate_simulator.py
```

Luego abre tu navegador en: **http://localhost:8080**

**Opción 2: Solo Video**
```bash
# Para ejecutar solo el procesamiento de video
cd ia_scripts
python gate_camera.py
```

---

## 🎮 CÓMO USAR EL SIMULADOR

### 🌐 Interfaz Web (http://localhost:8080)

1. **🚀 Iniciar Simulación:**
   - Haz clic en "▶️ Iniciar Simulación"
   - Se abrirá una ventana con el video `test_video.mp4`
   - El sistema detectará matrículas automáticamente

2. **⌨️ Controles del Video:**
   - `Q`: Salir del video
   - `R`: Reiniciar video desde el inicio
   - `ESPACIO`: Pausar/reanudar video

3. **📊 Información en Tiempo Real:**
   - **Estado del Gate:** CERRADO → ABRIENDO → ABIERTO → CERRANDO → CERRADO
   - **Detecciones:** Lista de placas detectadas con timestamps
   - **Eventos:** Historial de accesos permitidos/denegados

### 🎯 Flujo de Funcionamiento

1. **📹 Detección:** El sistema analiza frames del video
2. **🔍 Reconocimiento:** Detecta placas simuladas (ABC123, DEF456, etc.)
3. **📡 Consulta:** Envía placa al backend API
4. **✅/❌ Decisión:** Backend determina si permitir acceso
5. **🚪 Acción:** Gate se abre (permitido) o permanece cerrado (denegado)
6. **📊 Registro:** Se guarda evento en base de datos

---

## 📡 ENDPOINTS DE LA API

### 🚗 Control Vehicular por IA
```http
POST /api/seguridad/ia/control-vehicular/
Headers:
  X-API-KEY: MI_CLAVE_SUPER_SECRETA_12345
  Content-Type: application/json

Body:
{
  "placa": "ABC123",
  "tipo": "INGRESO"
}

Response 200 (Acceso Permitido):
{
  "evento_id": 15,
  "timestamp": "2025-10-02T10:30:45.123Z",
  "placa": "ABC123",
  "tipo_evento": "INGRESO",
  "accion": "PERMITIDO",
  "acceso_permitido": true,
  "motivo": "Vehículo autorizado para Casa 101",
  "vehiculo": {
    "tipo": "RESIDENTE",
    "propiedad": "Casa 101",
    "propiedad_id": 1,
    "autorizado": true
  },
  "mensaje": "✅ Acceso permitido para ABC123"
}

Response 403 (Acceso Denegado):
{
  "evento_id": 16,
  "timestamp": "2025-10-02T10:32:15.456Z",
  "placa": "XXX999",
  "tipo_evento": "INGRESO",
  "accion": "DENEGADO",
  "acceso_permitido": false,
  "motivo": "Placa 'XXX999' no encontrada.",
  "vehiculo": {
    "tipo": "NO_REGISTRADO",
    "autorizado": false
  },
  "mensaje": "❌ Acceso denegado para XXX999"
}
```

### 📊 Dashboard del Gate
```http
GET /api/seguridad/gate/dashboard/
Headers:
  Authorization: Token YOUR_TOKEN_HERE

Response:
{
  "timestamp": "2025-10-02T10:35:00.000Z",
  "estadisticas_hoy": {
    "total_eventos": 25,
    "accesos_permitidos": 18,
    "accesos_denegados": 7,
    "porcentaje_exito": 72.0
  },
  "vehiculos_registrados": {
    "total": 6,
    "residentes": 4,
    "visitantes": 0,
    "sin_asignar": 2
  },
  "ultimos_eventos": [
    {
      "id": 15,
      "timestamp": "2025-10-02T10:30:45.123Z",
      "placa": "ABC123",
      "tipo_evento": "INGRESO",
      "accion": "PERMITIDO",
      "motivo": "Vehículo autorizado para Casa 101",
      "vehiculo_info": "Residente - Casa 101",
      "tiempo_relativo": "Hace 5 minutos"
    }
  ]
}
```

---

## 🧪 PLACAS DE PRUEBA

### ✅ Placas Autorizadas (Residentes)
- **ABC123** → Casa 101 (Toyota Corolla)
- **DEF456** → Casa 102 (Honda Civic)
- **XYZ789** → Casa 103 (Chevrolet Spark)
- **LMN012** → Casa 104 (Nissan Sentra)

### ❌ Placas No Autorizadas
- **GHI345** → Registrada pero sin asignar
- **JKL678** → Registrada pero sin asignar
- **XXX999** → No registrada (cualquier otra placa)

### 🎭 Simulación de Detección
El simulador detecta aleatoriamente las placas autorizadas mientras procesa el video. Cada detección:
1. Se muestra en pantalla con colores (verde=permitido, rojo=denegado)
2. Se envía al backend para verificación
3. Se registra en la base de datos
4. Se actualiza en el dashboard web

---

## 📊 MONITOREO Y REPORTES

### 🖥️ Dashboard Web
- **URL:** http://localhost:8080
- **Características:**
  - Estado del gate en tiempo real
  - Lista de eventos recientes
  - Estadísticas del día
  - Control de simulación

### 🗄️ Base de Datos
- **Tabla:** `seguridad_eventoseguridad`
- **Campos principales:**
  - `fecha_hora`: Timestamp del evento
  - `placa_detectada`: Matrícula detectada
  - `accion`: PERMITIDO/DENEGADO
  - `tipo_evento`: INGRESO/SALIDA
  - `motivo`: Razón de la decisión

### 📱 API de Consulta
```bash
# Ver todos los eventos
curl -H "Authorization: Token YOUR_TOKEN" \
  http://127.0.0.1:8000/api/seguridad/eventos/

# Ver dashboard
curl -H "Authorization: Token YOUR_TOKEN" \
  http://127.0.0.1:8000/api/seguridad/gate/dashboard/
```

---

## 🔧 CONFIGURACIÓN AVANZADA

### 🎛️ Variables del Simulador
```python
# En gate_simulator.py
VIDEO_PATH = '../public/test_video.mp4'  # Ruta al video
API_BASE_URL = 'http://127.0.0.1:8000/api/seguridad/'  # URL del backend
API_KEY = "MI_CLAVE_SUPER_SECRETA_12345"  # Clave de API
WEB_PORT = 8080  # Puerto del dashboard web
```

### 🎥 Personalizar Detección
```python
# Cambiar frecuencia de detección
frame_skip = 30  # Procesar cada 30 frames (más alto = menos CPU)

# Cambiar placas simuladas
placas_simuladas = ['ABC123', 'DEF456', 'XYZ789', 'LMN012']

# Cambiar probabilidad de detección
if random.random() > 0.7:  # 30% de probabilidad
```

### 🗄️ Administrar Vehículos
```bash
# Agregar nuevos vehículos desde Django Admin
http://127.0.0.1:8000/admin/seguridad/vehiculo/

# O desde el shell de Django
python manage.py shell
>>> from seguridad.models import Vehiculo
>>> from condominio.models import Propiedad
>>> Vehiculo.objects.create(placa="NEW123", propiedad=Propiedad.objects.first())
```

---

## 🚨 SOLUCIÓN DE PROBLEMAS

### ❌ Error: Video no encontrado
```
Problema: Error: Video no encontrado en ../public/test_video.mp4
Solución: Verificar que test_video.mp4 esté en la carpeta public/
```

### ❌ Error de conexión con Backend
```
Problema: Error de conexión al backend
Solución: 
1. Verificar que Django esté corriendo: python manage.py runserver
2. Verificar URL en gate_simulator.py
3. Verificar API_KEY en settings.py
```

### ❌ Puerto 8080 ocupado
```
Problema: Puerto 8080 ya en uso
Solución: Cambiar WEB_PORT en gate_simulator.py a otro puerto (ej: 8081)
```

### 🐛 Debug de Detecciones
```python
# Activar logs detallados en gate_simulator.py
print(f"🔍 Frame {frame_count}: Buscando placas...")
print(f"📊 Regiones detectadas: {len(regiones)}")
```

---

## 🎯 CASOS DE USO REALES

### 1. 🏠 Acceso de Residente
```
1. Residente llega al gate
2. Cámara detecta placa "ABC123"
3. Sistema consulta base de datos
4. Encuentra que pertenece a Casa 101
5. Gate se abre automáticamente
6. Se registra evento de ingreso exitoso
```

### 2. 👥 Vehículo de Visitante
```
1. Visitante llega al gate
2. Cámara detecta placa "GHI345"
3. Sistema encuentra placa registrada pero sin asignar
4. Gate permanece cerrado
5. Guardia debe autorizar manualmente
6. Se registra evento de acceso denegado
```

### 3. 🚫 Vehículo No Autorizado
```
1. Vehículo desconocido llega
2. Cámara detecta placa "XXX999"
3. Sistema no encuentra la placa
4. Gate permanece cerrado
5. Se activa alerta de seguridad
6. Se registra evento de acceso denegado
```

---

## 📈 MÉTRICAS Y ESTADÍSTICAS

### 📊 KPIs del Sistema
- **Tasa de Reconocimiento:** % de placas detectadas correctamente
- **Tasa de Autorización:** % de accesos permitidos vs denegados
- **Tiempo de Respuesta:** Promedio de tiempo entre detección y respuesta
- **Disponibilidad:** % de tiempo que el sistema está operativo

### 📋 Reportes Disponibles
1. **Eventos por día/hora:** Análisis de tráfico vehicular
2. **Top vehículos:** Placas más frecuentes
3. **Eventos de seguridad:** Accesos denegados y alertas
4. **Performance del sistema:** Tiempos de respuesta y errores

---

## 🔜 PRÓXIMAS MEJORAS

### 🧠 IA Avanzada
- [ ] Integración con AWS Rekognition para OCR real
- [ ] Detección de tipo de vehículo (auto, moto, camión)
- [ ] Reconocimiento facial del conductor

### 📱 Aplicación Móvil
- [ ] App para residentes (ver histórico de accesos)
- [ ] Notificaciones push cuando llegan visitas
- [ ] Control remoto del gate

### 🏢 Integración Empresarial
- [ ] Conexión con sistemas de CCTV existentes
- [ ] API para sistemas de terceros
- [ ] Integración con ERP del condominio

---

**🎉 ¡Sistema de Reconocimiento Vehicular Listo para Usar!**

Con esta guía tienes todo lo necesario para implementar y usar el sistema de reconocimiento vehicular. El simulador te permite probar todas las funcionalidades usando el `test_video.mp4` sin necesidad de cámaras reales.