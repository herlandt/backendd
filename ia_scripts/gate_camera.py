# ia_system/gate_camera.py (Versión final con AWS y filtro)

import cv2
import requests
import re
import boto3

# --- CONFIGURACIÓN ---
VIDEO_PATH = 'test_video.mp4'
API_URL = 'https://smart-condominium-backend-cg7l.onrender.com/api/seguridad/ia/control-vehicular/'
API_KEY = "MI_CLAVE_SUPER_SECRETA_12345"
PROCESSED_PLATES = set()

# Inicializamos el cliente de Rekognition
try:
    rekognition_client = boto3.client('rekognition')
    print("Cliente de AWS Rekognition inicializado.")
except Exception as e:
    print(f"Error al inicializar el cliente de AWS. ¿Configuraste 'aws configure'? Error: {e}")
    exit()

# --- INICIAMOS EL PROCESAMIENTO DE VIDEO ---
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print("Error: No se pudo abrir el video.")
    exit()

print("Procesando video con AWS Rekognition... presiona 'q' para salir.")

frame_skip = 30  # Procesaremos 1 fotograma por segundo (aprox.) para ahorrar costos
frame_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    if frame_count % frame_skip != 0:
        cv2.imshow('Smart Condominium - Gate Camera (AWS AI)', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    # 1. Convertir el fotograma a bytes
    _, image_content_bytes = cv2.imencode('.jpg', frame)

    # 2. Llamar a la API de AWS Rekognition para detectar texto
    try:
        response = rekognition_client.detect_text(
            Image={'Bytes': image_content_bytes.tobytes()}
        )
        text_detections = response.get('TextDetections', [])

        for detection in text_detections:
            if detection['Type'] == 'LINE':
                text = detection['DetectedText']
                cleaned_text = re.sub(r'[\W_]+', '', text).upper()

                # 4. FILTRO INTELIGENTE:
                if (5 <= len(cleaned_text) <= 8 and
                    any(char.isdigit() for char in cleaned_text) and # Comprueba si tiene al menos un número
                    any(char.isalpha() for char in cleaned_text) and # Comprueba si tiene al menos una letra
                    cleaned_text not in PROCESSED_PLATES):
                    
                    print(f"Texto detectado por AWS: '{cleaned_text}'")
                    PROCESSED_PLATES.add(cleaned_text)

                    # 5. Enviar la placa a nuestra API de Django
                    try:
                        headers = {'X-API-KEY': API_KEY} # <-- Preparamos la cabecera
                        
                        # Añadimos la cabecera a la petición
                        api_response = requests.post(API_URL, json={'placa': cleaned_text}, headers=headers)
                        
                        if api_response.status_code == 200:
                            print(f"API Django dice: ACCESO PERMITIDO para {cleaned_text}")
                        elif api_response.status_code == 403:
                            print(f"API Django dice: ACCESO DENEGADO para {cleaned_text} (Razón: {api_response.json().get('detail')})")
                    except requests.exceptions.ConnectionError:
                        print("Error: No se pudo conectar a la API de Django.")
                                
    except Exception as e:
        print(f"Error al llamar a la API de Rekognition: {e}")
        if "Billing" in str(e):
            print("Error: La cuenta de AWS requiere facturación.")
            break

    cv2.imshow('Smart Condominium - Gate Camera (AWS AI)', frame)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

# --- LIMPIEZA ---
cap.release()
cv2.destroyAllWindows()
print("Procesamiento de video terminado.")