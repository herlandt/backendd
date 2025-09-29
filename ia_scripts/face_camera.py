# ia_scripts/face_camera.py

import cv2
import requests
import os
import time

# --- CONFIGURACIÓN ---
API_URL = 'https://smart-condominium-backend-cg7l.onrender.com/api/seguridad/ia/verificar-rostro/'
API_KEY = "MI_CLAVE_SUPER_SECRETA_12345" # La misma clave que usamos para las matrículas
LAST_REQUEST_TIME = 0
REQUEST_COOLDOWN = 5 # Segundos de espera entre peticiones para no saturar

# --- Cargar el clasificador de rostros de OpenCV ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FACE_CASCADE_PATH = os.path.join(SCRIPT_DIR, 'haarcascade_frontalface_default.xml')

# --- IMPORTANTE ---
# Debes descargar el archivo 'haarcascade_frontalface_default.xml' y guardarlo
# en la misma carpeta 'ia_scripts/'.
# Puedes descargarlo desde aquí: 
# https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml

if not os.path.exists(FACE_CASCADE_PATH):
    print(f"ERROR: No se encuentra el archivo 'haarcascade_frontalface_default.xml' en la carpeta {SCRIPT_DIR}")
    exit()

face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)

# --- INICIAR CÁMARA ---
cap = cv2.VideoCapture(0) # Usamos la webcam
if not cap.isOpened():
    print("Error: No se pudo abrir la cámara.")
    exit()

print("Iniciando cámara para reconocimiento facial... presiona 'q' para salir.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

    current_time = time.time()
    
    # Solo procesamos si hay caras y ha pasado el tiempo de espera
    if len(faces) > 0 and (current_time - LAST_REQUEST_TIME) > REQUEST_COOLDOWN:
        (x, y, w, h) = faces[0] # Tomamos solo la primera cara detectada
        
        # Extraer solo el rostro
        face_roi = frame[y:y+h, x:x+w]
        
        # Convertir el rostro a formato de imagen para enviar
        is_success, im_buf_arr = cv2.imencode(".jpg", face_roi)
        if is_success:
            image_bytes = im_buf_arr.tobytes()

            # Enviar el rostro a la API para verificación
            try:
                print("Enviando rostro para verificación...")
                headers = {'X-API-KEY': API_KEY}
                files = {'foto': ('face.jpg', image_bytes, 'image/jpeg')}
                
                api_response = requests.post(API_URL, files=files, headers=headers, timeout=5)

                response_data = api_response.json()
                print(f"Respuesta de la API: {response_data.get('detail', 'Error')}")
                LAST_REQUEST_TIME = time.time() # Reiniciamos el contador

            except requests.exceptions.RequestException as e:
                print(f"Error al conectar con la API: {e}")
                LAST_REQUEST_TIME = time.time()

    # Dibujamos los rectángulos en cada fotograma
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

    cv2.imshow('Smart Condominium - Face Recognition', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- LIMPIEZA ---
cap.release()
cv2.destroyAllWindows()