# 🎯 SOLUCIÓN INMEDIATA PARA TU FRONTEND REACT

## ✅ **CONFIRMACIÓN DEL BACKEND**

Tu backend Django está funcionando perfectamente:
- ✅ Endpoint `/api/seguridad/ia/control-vehicular/` responde correctamente
- ✅ API Key `MI_CLAVE_SUPER_SECRETA_12345` funciona
- ✅ Validaciones y respuestas correctas

## 🔧 **CÓDIGO DE SOLUCIÓN PARA REACT**

### 1. **Configurar Cliente HTTP con API Key**

```typescript
// En tu archivo api.ts o donde tengas axios configurado
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5175/api', // Ajusta tu URL base
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'X-API-KEY': 'MI_CLAVE_SUPER_SECRETA_12345' // ← ESTO ES LO QUE FALTABA
  }
});

// Interceptors para debugging (opcional pero útil)
api.interceptors.request.use(
  (config) => {
    console.log('🌐', config.method?.toUpperCase(), config.url);
    return config;
  }
);

api.interceptors.response.use(
  (response) => {
    console.log('✅', response.status, response.config.method?.toUpperCase(), response.config.url);
    return response;
  },
  (error) => {
    console.error('❌', error.response?.status, 'Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default api;
```

### 2. **Función de Control Vehicular Corregida**

```typescript
// En tu archivo de servicios API
export async function controlVehicularIA(placa: string, tipo: 'INGRESO' | 'SALIDA' = 'INGRESO') {
  try {
    // Validar entrada
    if (!placa || placa.trim().length === 0) {
      throw new Error('La placa es requerida');
    }
    
    const { data } = await api.post('/seguridad/ia/control-vehicular/', {
      placa: placa.toUpperCase().trim(),
      tipo: tipo.toUpperCase()
    });
    
    return data;
  } catch (error: any) {
    console.error('Error en control vehicular:', error);
    
    if (error.response?.status === 403) {
      throw new Error('Acceso denegado - Verificar API Key');
    } else if (error.response?.status === 400) {
      throw new Error(error.response.data?.error || 'Datos inválidos');
    }
    
    throw error;
  }
}
```

### 3. **Componente React Corregido**

```tsx
// En tu componente VehicleTestingPage.tsx
import React, { useState } from 'react';
import { controlVehicularIA } from './api'; // Ajusta la ruta

export const VehicleTestingPage: React.FC = () => {
  const [placa, setPlaca] = useState('');
  const [resultado, setResultado] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleVerificarPlaca = async () => {
    if (!placa.trim()) {
      setError('Por favor ingresa una placa');
      return;
    }

    setLoading(true);
    setError(null);
    setResultado(null);

    try {
      console.log('🔍 Verificando placa:', placa);
      const response = await controlVehicularIA(placa, 'INGRESO');
      
      console.log('📊 Respuesta del servidor:', response);
      setResultado(response);
      
    } catch (err: any) {
      console.error('❌ Error:', err);
      setError(err.message || 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="vehicle-testing-page">
      <h2>🚗 Prueba de Control Vehicular</h2>
      
      <div className="input-section">
        <input
          type="text"
          value={placa}
          onChange={(e) => setPlaca(e.target.value.toUpperCase())}
          placeholder="Ingresa la placa (ej: ABC123)"
          maxLength={10}
        />
        
        <button
          onClick={handleVerificarPlaca}
          disabled={loading || !placa.trim()}
        >
          {loading ? '🔄 Verificando...' : '🔍 Verificar Placa'}
        </button>
      </div>

      {error && (
        <div className="error-message" style={{ color: 'red', margin: '10px 0' }}>
          ❌ {error}
        </div>
      )}

      {resultado && (
        <div className="resultado-section">
          <h3>📋 Resultado:</h3>
          
          <div className={`resultado-card ${resultado.acceso_permitido ? 'permitido' : 'denegado'}`}>
            <p><strong>Placa:</strong> {resultado.placa}</p>
            <p><strong>Estado:</strong> {resultado.acceso_permitido ? '✅ PERMITIDO' : '❌ DENEGADO'}</p>
            <p><strong>Motivo:</strong> {resultado.motivo}</p>
            
            {resultado.vehiculo && (
              <div className="vehiculo-info">
                <p><strong>Tipo:</strong> {resultado.vehiculo.tipo}</p>
                {resultado.vehiculo.propiedad && (
                  <p><strong>Propiedad:</strong> {resultado.vehiculo.propiedad}</p>
                )}
              </div>
            )}
            
            <p><strong>Timestamp:</strong> {new Date(resultado.timestamp).toLocaleString()}</p>
          </div>
        </div>
      )}

      <div className="placas-test">
        <h4>🧪 Placas de Prueba:</h4>
        <div className="test-buttons">
          <button onClick={() => setPlaca('ABC123')}>ABC123 (Autorizada)</button>
          <button onClick={() => setPlaca('DEF456')}>DEF456 (Autorizada)</button>
          <button onClick={() => setPlaca('XXX999')}>XXX999 (No registrada)</button>
          <button onClick={() => setPlaca('GHI345')}>GHI345 (Sin asignar)</button>
        </div>
      </div>
    </div>
  );
};
```

### 4. **CSS para el Componente**

```css
/* Estilos para el componente */
.vehicle-testing-page {
  max-width: 600px;
  margin: 20px auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

.input-section {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.input-section input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 16px;
}

.input-section button {
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
}

.input-section button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.resultado-card {
  padding: 15px;
  border-radius: 8px;
  margin: 10px 0;
}

.resultado-card.permitido {
  background: #d4edda;
  border: 1px solid #c3e6cb;
}

.resultado-card.denegado {
  background: #f8d7da;
  border: 1px solid #f5c6cb;
}

.test-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.test-buttons button {
  padding: 8px 12px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.test-buttons button:hover {
  background: #5a6268;
}
```

---

## 🛠️ **SOLUCIÓN PARA VideoProcessor (FormData/Blob)**

```tsx
// VideoProcessor.tsx corregido
import React, { useRef, useEffect, useState } from 'react';

interface VideoProcessorProps {
  videoSrc: string;
  onPlateDetected?: (placa: string) => void;
}

export const VideoProcessor: React.FC<VideoProcessorProps> = ({ 
  videoSrc, 
  onPlateDetected 
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const processFrame = async () => {
    if (!videoRef.current || !canvasRef.current || isProcessing) return;
    
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    if (!ctx || video.paused || video.ended) return;
    
    setIsProcessing(true);
    
    try {
      // Configurar canvas con las dimensiones del video
      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 480;
      
      // Dibujar frame actual
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // Convertir canvas a Blob usando Promise
      const blob = await new Promise<Blob>((resolve, reject) => {
        canvas.toBlob((blob) => {
          if (blob) {
            resolve(blob);
          } else {
            reject(new Error('No se pudo crear blob desde canvas'));
          }
        }, 'image/jpeg', 0.8);
      });
      
      console.log('✅ Blob creado:', blob.size, 'bytes');
      
      // Crear FormData correctamente
      const formData = new FormData();
      formData.append('frame', blob, 'frame.jpg');
      
      // Aquí enviarías al endpoint de procesamiento
      // const response = await api.post('/seguridad/ia/procesar-frame/', formData, {
      //   headers: {
      //     'X-API-KEY': 'MI_CLAVE_SUPER_SECRETA_12345'
      //     // NO incluir Content-Type, axios lo detecta automáticamente para FormData
      //   }
      // });
      
      // Simulación de detección para demo
      const placasSimuladas = ['ABC123', 'DEF456', 'XXX999', 'GHI345'];
      if (Math.random() > 0.8) { // 20% de probabilidad
        const placaDetectada = placasSimuladas[Math.floor(Math.random() * placasSimuladas.length)];
        console.log('🔍 Placa simulada detectada:', placaDetectada);
        onPlateDetected?.(placaDetectada);
      }
      
    } catch (error) {
      console.error('❌ Error procesando frame:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  useEffect(() => {
    // Procesar frame cada 3 segundos
    intervalRef.current = setInterval(() => {
      processFrame();
    }, 3000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return (
    <div className="video-processor">
      <video
        ref={videoRef}
        src={videoSrc}
        autoPlay
        loop
        muted
        style={{ 
          maxWidth: '100%', 
          border: '2px solid #ddd',
          borderRadius: '8px'
        }}
        onLoadedMetadata={() => {
          console.log('📹 Video cargado:', {
            width: videoRef.current?.videoWidth,
            height: videoRef.current?.videoHeight
          });
        }}
      />
      
      <canvas
        ref={canvasRef}
        style={{ display: 'none' }}
      />
      
      <div style={{ marginTop: '10px', padding: '10px', background: '#f8f9fa', borderRadius: '5px' }}>
        <p>
          📊 Estado: {isProcessing ? '🔄 Procesando frame...' : '⏳ Esperando próximo frame'}
        </p>
        <p style={{ fontSize: '12px', color: '#666' }}>
          💡 El sistema simula detección de placas cada 3 segundos
        </p>
      </div>
    </div>
  );
};
```

---

## ✅ **CHECKLIST FINAL**

- [ ] ✅ **API Key agregada** a headers globales en axios
- [ ] ✅ **Función controlVehicularIA** corregida con manejo de errores
- [ ] ✅ **VideoProcessor** con conversión Blob correcta
- [ ] ✅ **Componente de pruebas** funcional
- [ ] ✅ **CSS básico** para visualización

---

## 🧪 **PRUEBA INMEDIATA**

1. **Copia y pega** el código de configuración de API con la API key
2. **Reinicia tu aplicación React**
3. **Abre la consola** del navegador (F12)
4. **Prueba con placa "ABC123"** - debería devolver status 200
5. **Revisa los logs** en la consola

**¡Con estos cambios tu aplicación debería funcionar sin errores 403!** 🚀