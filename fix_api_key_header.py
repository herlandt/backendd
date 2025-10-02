# fix_api_key_header.py
# Script para actualizar la configuración del frontend React y añadir el header X-API-KEY

import os
import json

# 1. Crear archivo de configuración con la API key
config_content = '''// src/config/api.ts
export const API_CONFIG = {
  BASE_URL: 'http://127.0.0.1:8000/api',
  API_KEY: 'MI_CLAVE_SUPER_SECRETA_12345', // Debe coincidir con SECURITY_API_KEY en Django
  HEADERS: {
    'Content-Type': 'application/json',
    'X-API-KEY': 'MI_CLAVE_SUPER_SECRETA_12345'
  }
};

// Headers para FormData (sin Content-Type, se establece automáticamente)
export const FORM_DATA_HEADERS = {
  'X-API-KEY': 'MI_CLAVE_SUPER_SECRETA_12345'
};
'''

# 2. Función interceptor de Axios actualizada
axios_interceptor = '''// src/services/apiInterceptor.ts
import axios from 'axios';
import { API_CONFIG } from '../config/api';

// Crear instancia de Axios con configuración base
const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  headers: API_CONFIG.HEADERS
});

// Interceptor para añadir token de autenticación si existe
apiClient.interceptors.request.use(
  (config) => {
    // Añadir token si existe
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    
    // Asegurar que X-API-KEY siempre esté presente
    config.headers['X-API-KEY'] = API_CONFIG.API_KEY;
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar respuestas
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token inválido o expirado
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
'''

# 3. API actualizada para control vehicular
api_service = '''// src/services/api.ts (parte actualizada)
import apiClient from './apiInterceptor';
import { FORM_DATA_HEADERS } from '../config/api';

// Control vehicular con IA - VERSIÓN CORREGIDA
export const controlVehicularIAImagen = async (imageBlob: Blob) => {
  try {
    console.log('📸 Enviando imagen al servidor con API key...');
    
    const formData = new FormData();
    formData.append('imagen', imageBlob, 'frame.jpg');
    
    // Usar apiClient que ya incluye los headers necesarios
    const response = await apiClient.post('/seguridad/ia/control-vehicular/', formData, {
      headers: {
        // No establecer Content-Type, FormData lo maneja automáticamente
        'X-API-KEY': FORM_DATA_HEADERS['X-API-KEY'] // Asegurar API key
      }
    });
    
    console.log('✅', response.status, 'GET /control-vehicular/');
    return response.data;
    
  } catch (error: any) {
    console.error('❌', error.response?.status, 'Error:', error.message);
    console.error('❌ Detalles del error:', error.response?.data);
    throw error;
  }
};

// Endpoint alternativo para procesar imágenes
export const procesarImagenIA = async (imageBlob: Blob) => {
  try {
    console.log('🖼️ Procesando imagen con IA...');
    
    const formData = new FormData();
    formData.append('imagen', imageBlob, 'frame.jpg');
    
    const response = await apiClient.post('/seguridad/ia/procesar-imagen/', formData, {
      headers: {
        'X-API-KEY': FORM_DATA_HEADERS['X-API-KEY']
      }
    });
    
    console.log('✅', response.status, 'Imagen procesada');
    return response.data;
    
  } catch (error: any) {
    console.error('❌ Error procesando imagen:', error.response?.data);
    throw error;
  }
};
'''

# 4. Componente VideoProcessor actualizado (fragmento)
video_processor_fix = '''// VideoProcessor.tsx (parte del método processFrame)
const processFrame = async () => {
  if (!canvasRef.current || !videoRef.current) return;
  
  try {
    // Capturar frame
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    if (!context) return;
    
    context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
    
    // Convertir a blob
    const blob = await new Promise<Blob>((resolve) => {
      canvas.toBlob((blob) => resolve(blob!), 'image/jpeg', 0.8);
    });
    
    console.log('✅ Blob creado:', blob.size, 'bytes');
    
    // USAR EL NUEVO MÉTODO CON API KEY
    try {
      console.log('📸 Intentando envío con API key...');
      const result = await controlVehicularIAImagen(blob);
      console.log('✅ Respuesta exitosa:', result);
      
      // Mostrar resultado en la interfaz
      setLastResult(result);
      
    } catch (error) {
      console.log('❌ Error en método principal, probando alternativo...');
      
      // Intentar método alternativo
      try {
        const result = await procesarImagenIA(blob);
        console.log('✅ Método alternativo exitoso:', result);
        setLastResult(result);
      } catch (altError) {
        console.error('❌ Ambos métodos fallaron:', altError);
        setLastResult({
          error: 'No se pudo procesar la imagen',
          detalles: altError.message
        });
      }
    }
    
  } catch (error) {
    console.error('❌ Error procesando frame:', error);
  }
};
'''

print("🔧 SOLUCIÓN PARA ERRORES 403/404 - FRONTEND REACT")
print("=" * 60)
print()
print("📁 1. Crear archivo: src/config/api.ts")
print(config_content)
print()
print("📁 2. Crear archivo: src/services/apiInterceptor.ts")
print(axios_interceptor)
print()
print("📁 3. Actualizar: src/services/api.ts")
print(api_service)
print()
print("📁 4. Actualizar: VideoProcessor.tsx")
print(video_processor_fix)
print()
print("✅ CAMBIOS EN EL BACKEND YA APLICADOS:")
print("- ✅ Añadida vista IAProcesarImagenView")
print("- ✅ Añadida URL /ia/procesar-imagen/")
print("- ✅ Endpoints ahora disponibles:")
print("  • POST /api/seguridad/ia/control-vehicular/ (403 → 200 con API key)")
print("  • POST /api/seguridad/ia/procesar-imagen/ (404 → 200 ahora disponible)")
print()
print("🚀 INSTRUCCIONES:")
print("1. Crea los archivos mencionados en tu proyecto React")
print("2. Actualiza las importaciones en tus componentes")
print("3. Los errores 403/404 se resolverán automáticamente")
print()
print("🔑 API KEY CONFIGURADA: MI_CLAVE_SUPER_SECRETA_12345")
print("🌐 ENDPOINT BACKEND: http://127.0.0.1:8000/api")