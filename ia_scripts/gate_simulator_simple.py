#!/usr/bin/env python3
"""
🚗 SIMULADOR SIMPLE DE GATE VEHICULAR
Procesa test_video.mp4 y simula el control de acceso vehicular
"""

import cv2
import requests
import os
import json
import time
import threading
import random
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler

# CONFIGURACION
VIDEO_PATH = '../public/test_video.mp4'
API_BASE_URL = 'http://127.0.0.1:8000/api/seguridad/'
API_KEY = "MI_CLAVE_SUPER_SECRETA_12345"
WEB_PORT = 8080

# ESTADO GLOBAL
SISTEMA_ESTADO = {
    'activo': False,
    'video_procesando': False,
    'ultima_deteccion': None,
    'eventos_recientes': [],
    'gate_estado': 'CERRADO'
}

class GateSimulator:
    def __init__(self):
        self.cap = None
        self.frame_count = 0
        self.frame_skip = 30
        
    def inicializar_video(self):
        """Inicializa la captura de video"""
        if not os.path.exists(VIDEO_PATH):
            print(f"❌ Error: Video no encontrado en {VIDEO_PATH}")
            return False
            
        self.cap = cv2.VideoCapture(VIDEO_PATH)
        if not self.cap.isOpened():
            print("❌ Error: No se pudo abrir el video")
            return False
            
        print(f"✅ Video inicializado: {VIDEO_PATH}")
        return True
    
    def detectar_placa_simulada(self):
        """Simula detección de placas"""
        placas_simuladas = ['ABC123', 'DEF456', 'XYZ789', 'LMN012', 'GHI345', 'XXX999']
        
        # 20% de probabilidad de detectar placa
        if random.random() > 0.8:
            return random.choice(placas_simuladas)
        return None
    
    def enviar_a_backend(self, placa, tipo_evento='INGRESO'):
        """Envia la placa detectada al backend"""
        url = f"{API_BASE_URL}ia/control-vehicular/"
        headers = {
            'X-API-KEY': API_KEY,
            'Content-Type': 'application/json'
        }
        data = {
            'placa': placa,
            'tipo': tipo_evento
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=5)
            return response.status_code, response.json()
        except Exception as e:
            return None, {'error': str(e)}
    
    def simular_apertura_gate(self):
        """Simula la secuencia de apertura del gate"""
        def secuencia():
            SISTEMA_ESTADO['gate_estado'] = 'ABRIENDO'
            time.sleep(2)
            SISTEMA_ESTADO['gate_estado'] = 'ABIERTO'
            time.sleep(5)
            SISTEMA_ESTADO['gate_estado'] = 'CERRANDO'
            time.sleep(2)
            SISTEMA_ESTADO['gate_estado'] = 'CERRADO'
        
        threading.Thread(target=secuencia, daemon=True).start()
    
    def procesar_frame(self, frame):
        """Procesa un frame del video"""
        # Detectar placa simulada
        placa = self.detectar_placa_simulada()
        
        if placa:
            print(f"🔍 Placa detectada: {placa}")
            
            # Enviar al backend
            status_code, response = self.enviar_a_backend(placa)
            
            # Actualizar estado global
            evento = {
                'timestamp': datetime.now().isoformat(),
                'placa': placa,
                'status_code': status_code,
                'response': response,
                'accion': 'PERMITIDO' if status_code == 200 else 'DENEGADO'
            }
            
            SISTEMA_ESTADO['ultima_deteccion'] = evento
            SISTEMA_ESTADO['eventos_recientes'].insert(0, evento)
            
            # Mantener solo los últimos 10 eventos
            if len(SISTEMA_ESTADO['eventos_recientes']) > 10:
                SISTEMA_ESTADO['eventos_recientes'] = SISTEMA_ESTADO['eventos_recientes'][:10]
            
            # Simular apertura del gate si es permitido
            if status_code == 200:
                self.simular_apertura_gate()
            
            # Dibujar información en el frame
            color = (0, 255, 0) if status_code == 200 else (0, 0, 255)
            cv2.putText(frame, f"PLACA: {placa}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            cv2.putText(frame, f"ESTADO: {evento['accion']}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            # Mensaje de respuesta
            mensaje = response.get('mensaje', 'Sin mensaje')
            cv2.putText(frame, mensaje[:50], (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Estado del gate
        gate_color = (255, 255, 255)
        if SISTEMA_ESTADO['gate_estado'] == 'ABIERTO':
            gate_color = (0, 255, 0)
        elif SISTEMA_ESTADO['gate_estado'] in ['ABRIENDO', 'CERRANDO']:
            gate_color = (0, 255, 255)
        
        cv2.putText(frame, f"GATE: {SISTEMA_ESTADO['gate_estado']}", 
                   (10, frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, gate_color, 2)
        
        return frame
    
    def iniciar_procesamiento(self):
        """Inicia el procesamiento del video"""
        if not self.inicializar_video():
            return False
        
        print("🎥 Iniciando procesamiento de video...")
        print("   Presiona 'q' para detener")
        print("   Presiona 'r' para reiniciar video")
        print("   Presiona ESPACIO para pausar/reanudar")
        
        SISTEMA_ESTADO['activo'] = True
        SISTEMA_ESTADO['video_procesando'] = True
        paused = False
        
        while SISTEMA_ESTADO['activo']:
            if not paused:
                ret, frame = self.cap.read()
                if not ret:
                    # Reiniciar video
                    print("🔄 Reiniciando video...")
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                
                self.frame_count += 1
                
                # Procesar solo cada N frames
                if self.frame_count % self.frame_skip == 0:
                    frame = self.procesar_frame(frame)
                
                # Mostrar frame
                cv2.imshow('🚗 Smart Condominium - Gate Simulator', frame)
            
            # Manejar teclas
            key = cv2.waitKey(30) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.frame_count = 0
                print("🔄 Video reiniciado")
            elif key == ord(' '):
                paused = not paused
                print(f"⏸️ Video {'pausado' if paused else 'reanudado'}")
        
        # Limpiar
        SISTEMA_ESTADO['activo'] = False
        SISTEMA_ESTADO['video_procesando'] = False
        self.cap.release()
        cv2.destroyAllWindows()
        print("🛑 Simulador detenido")

# SERVIDOR WEB
class GateWebHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_dashboard_html().encode())
        elif self.path == '/api/estado':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(SISTEMA_ESTADO).encode())
        elif self.path == '/api/iniciar':
            if not SISTEMA_ESTADO['video_procesando']:
                threading.Thread(target=self.iniciar_simulador, daemon=True).start()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'iniciado'}).encode())
        elif self.path == '/api/detener':
            SISTEMA_ESTADO['activo'] = False
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'detenido'}).encode())
        else:
            super().do_GET()
    
    def iniciar_simulador(self):
        simulator = GateSimulator()
        simulator.iniciar_procesamiento()
    
    def get_dashboard_html(self):
        return '''
<!DOCTYPE html>
<html>
<head>
    <title>🚗 Gate Simulator</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 10px; text-align: center; }
        .controls { background: white; padding: 20px; margin: 20px 0; border-radius: 10px; }
        .status { background: white; padding: 20px; margin: 20px 0; border-radius: 10px; }
        .eventos { background: white; padding: 20px; margin: 20px 0; border-radius: 10px; max-height: 400px; overflow-y: auto; }
        button { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        .btn-start { background: #27ae60; color: white; }
        .btn-stop { background: #e74c3c; color: white; }
        .gate-status { font-size: 24px; font-weight: bold; padding: 10px; border-radius: 5px; text-align: center; margin: 10px 0; }
        .gate-cerrado { background: #e74c3c; color: white; }
        .gate-abierto { background: #27ae60; color: white; }
        .gate-moviendo { background: #f39c12; color: white; }
        .evento { padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 5px solid #3498db; }
        .evento-permitido { border-left-color: #27ae60; background: #d5f4e6; }
        .evento-denegado { border-left-color: #e74c3c; background: #fadbd8; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚗 Smart Condominium - Gate Simulator</h1>
            <p>Sistema de Reconocimiento Vehicular con test_video.mp4</p>
        </div>
        
        <div class="controls">
            <h3>🎮 Controles del Simulador</h3>
            <button class="btn-start" onclick="iniciarSimulador()">▶️ Iniciar Simulación</button>
            <button class="btn-stop" onclick="detenerSimulador()">⏹️ Detener Simulación</button>
            <p><strong>Instrucciones de Video:</strong></p>
            <ul>
                <li>Presiona <kbd>Q</kbd> para salir del video</li>
                <li>Presiona <kbd>R</kbd> para reiniciar el video</li>
                <li>Presiona <kbd>ESPACIO</kbd> para pausar/reanudar</li>
            </ul>
        </div>
        
        <div class="status">
            <h3>📊 Estado del Sistema</h3>
            <div class="gate-status" id="gateStatus">GATE: CERRADO</div>
            <p><strong>Sistema Activo:</strong> <span id="sistemaActivo">No</span></p>
            <p><strong>Video Procesando:</strong> <span id="videoProcesando">No</span></p>
            <p><strong>Última Detección:</strong> <span id="ultimaDeteccion">Ninguna</span></p>
        </div>
        
        <div class="eventos">
            <h3>📋 Eventos Recientes</h3>
            <div id="eventosRecientes">No hay eventos</div>
        </div>
    </div>

    <script>
        function actualizarEstado() {
            fetch('/api/estado')
                .then(response => response.json())
                .then(data => {
                    // Estado del gate
                    const gateElement = document.getElementById('gateStatus');
                    gateElement.textContent = `GATE: ${data.gate_estado}`;
                    gateElement.className = 'gate-status ';
                    
                    if (data.gate_estado === 'CERRADO') {
                        gateElement.className += 'gate-cerrado';
                    } else if (data.gate_estado === 'ABIERTO') {
                        gateElement.className += 'gate-abierto';
                    } else {
                        gateElement.className += 'gate-moviendo';
                    }
                    
                    // Estado del sistema
                    document.getElementById('sistemaActivo').textContent = data.activo ? 'Sí' : 'No';
                    document.getElementById('videoProcesando').textContent = data.video_procesando ? 'Sí' : 'No';
                    
                    // Última detección
                    if (data.ultima_deteccion) {
                        const fecha = new Date(data.ultima_deteccion.timestamp).toLocaleTimeString();
                        document.getElementById('ultimaDeteccion').textContent = 
                            `${data.ultima_deteccion.placa} (${fecha})`;
                    }
                    
                    // Eventos recientes
                    const eventosDiv = document.getElementById('eventosRecientes');
                    if (data.eventos_recientes && data.eventos_recientes.length > 0) {
                        eventosDiv.innerHTML = data.eventos_recientes.map(evento => {
                            const fecha = new Date(evento.timestamp).toLocaleTimeString();
                            const clase = evento.accion === 'PERMITIDO' ? 'evento-permitido' : 'evento-denegado';
                            return `
                                <div class="evento ${clase}">
                                    <strong>${evento.placa}</strong> - ${evento.accion} (${fecha})
                                    <br><small>Status: ${evento.status_code} | ${JSON.stringify(evento.response.mensaje || 'Sin mensaje')}</small>
                                </div>
                            `;
                        }).join('');
                    } else {
                        eventosDiv.innerHTML = 'No hay eventos';
                    }
                })
                .catch(error => console.error('Error:', error));
        }
        
        function iniciarSimulador() {
            fetch('/api/iniciar')
                .then(response => response.json())
                .then(data => {
                    console.log('Simulador iniciado:', data);
                    alert('Simulador iniciado. Se abrirá la ventana de video.');
                });
        }
        
        function detenerSimulador() {
            fetch('/api/detener')
                .then(response => response.json())
                .then(data => {
                    console.log('Simulador detenido:', data);
                });
        }
        
        // Actualizar estado cada 2 segundos
        setInterval(actualizarEstado, 2000);
        
        // Actualizar al cargar la página
        actualizarEstado();
    </script>
</body>
</html>
        '''

def main():
    print("🚗 SMART CONDOMINIUM - GATE SIMULATOR")
    print("=" * 50)
    print("🌐 Iniciando servidor web en http://localhost:8080")
    print("🎥 El simulador procesará public/test_video.mp4")
    print("📡 Conectará con API en http://127.0.0.1:8000")
    print("")
    
    try:
        httpd = HTTPServer(('localhost', WEB_PORT), GateWebHandler)
        print(f"✅ Servidor web iniciado en http://localhost:{WEB_PORT}")
        print("   Abre tu navegador y ve a esa dirección")
        print("   Presiona Ctrl+C para detener")
        print("")
        
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()