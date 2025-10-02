# 🏢 BACKEND SISTEMA DE CONDOMINIO

## 📁 **ORGANIZACIÓN DE CARPETAS**

Para evitar confusiones entre equipos, los archivos de frontend han sido organizados en carpetas específicas:

---

## 📱 **EQUIPO MÓVIL** → `equipo_movil/`

**🎯 Para:** Desarrollo de aplicación Flutter  
**📱 Contiene:** 
- Usuarios sincronizados con app móvil
- Scripts de conectividad para emuladores Android
- Análisis de compatibilidad móvil
- Configuración específica para Flutter

**🚀 Comenzar:** `cd equipo_movil && python crear_usuarios_movil_sincronizado.py`

---

## 🌐 **EQUIPO WEB** → `equipo_web/`

**🎯 Para:** Desarrollo de aplicaciones React/Next.js  
**💻 Contiene:**
- Guías completas de desarrollo web
- Scripts de usuarios para frontend web
- Documentación de APIs
- Configuración específica para React

**🚀 Comenzar:** `cd equipo_web && python crear_usuarios_frontend.py`

---

## 📄 **ARCHIVOS COMPARTIDOS (RAÍZ)**

### **🔧 ESQUEMAS Y DOCUMENTACIÓN:**
- **`openapi_schema_actualizado_2025.yaml`** - Schema OpenAPI completo
- **`SCHEMA_COMPLETO_ACTUALIZADO_2025.md`** - Documentación del schema

### **⚙️ BACKEND DJANGO:**
- **`manage.py`** - Comando principal de Django
- **`config/`** - Configuración del backend
- **Apps Django:** `usuarios/`, `condominio/`, `finanzas/`, etc.

### **🗄️ BASE DE DATOS:**
- **`db.sqlite3`** - Base de datos de desarrollo

---

## 🚀 **COMANDOS PRINCIPALES**

### **📱 PARA EQUIPO MÓVIL:**
```bash
# 1. Iniciar backend
python manage.py runserver 0.0.0.0:8000

# 2. Configurar usuarios móvil
cd equipo_movil
python crear_usuarios_movil_sincronizado.py

# 3. Probar conectividad
python test_conectividad_movil.py
```

### **🌐 PARA EQUIPO WEB:**
```bash
# 1. Iniciar backend  
python manage.py runserver 0.0.0.0:8000

# 2. Configurar usuarios web
cd equipo_web
python crear_usuarios_frontend.py

# 3. Comenzar desarrollo
# Usar documentación en equipo_web/
```

---

## 🔗 **URLS DE CONEXIÓN**

### **📱 MÓVIL (Flutter):**
- **Android Emulator:** `http://10.0.2.2:8000/api/`
- **Red Local:** `http://192.168.0.5:8000/api/`

### **🌐 WEB (React/Next.js):**
- **Desarrollo Local:** `http://127.0.0.1:8000/api/`
- **Localhost:** `http://localhost:8000/api/`

---

## 👥 **USUARIOS DE PRUEBA**

### **📱 MÓVIL (Sincronizados):**
```
admin / admin123
residente1 / isaelOrtiz2
propietario1 / joseGarcia3
inquilino1 / anaLopez4
seguridad1 / guardia123
mantenimiento1 / mant456
invitado1 / invCarlos5
```

### **🌐 WEB (Estándar):**
```
admin / admin123
residente1 / isaelOrtiz2
residente2 / maria123
seguridad1 / guardia123
electricista1 / tecnico123
plomero1 / plomero123
mantenimiento1 / mant123
```

---

## ✅ **ESTADO ACTUAL**

- **✅ Backend:** 100% operativo
- **✅ Móvil:** Usuarios sincronizados y verificados
- **✅ Web:** Documentación completa y scripts listos
- **✅ CORS:** Configurado para ambos equipos
- **✅ Schemas:** Actualizados y documentados

---

## 📞 **SOPORTE**

### **🤝 COORDINACIÓN:**
- **Issues técnicos:** Documentar en el repositorio
- **Cambios de API:** Comunicar previamente
- **Testing conjunto:** Coordinar con backend team

### **📚 DOCUMENTACIÓN:**
- **Móvil:** Ver `equipo_movil/README.md`
- **Web:** Ver `equipo_web/README.md`
- **Backend:** Este archivo

---

## 🎯 **PRÓXIMOS PASOS**

1. **📱 Equipo Móvil:** Leer `equipo_movil/README.md` y comenzar desarrollo
2. **🌐 Equipo Web:** Leer `equipo_web/README.md` y comenzar desarrollo  
3. **🔧 Backend:** Mantener servidor corriendo y dar soporte

---

**📅 Organizado:** Octubre 2, 2025  
**🎯 Propósito:** Evitar confusiones entre equipos  
**✅ Estado:** Listo para desarrollo paralelo