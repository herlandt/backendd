import cv2
import time

RTSP_URL = "rtsp://127.0.0.1:8554/cam1"

print(f"Intentando conectar a: {RTSP_URL}")
# Usamos cv2.CAP_FFMPEG para ser explícitos
cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)

# Esperamos un momento para que se establezca la conexión
time.sleep(2)

if not cap.isOpened():
    print("\n❌ ERROR: ¡No se pudo abrir el stream de video!")
    print("Posibles causas:")
    print("1. ¿El contenedor de MediaMTX (Terminal 1) está corriendo?")
    print("2. ¿El comando de FFMPEG (Terminal 2) está corriendo y transmitiendo?")
    print("3. Revisa el Firewall de Windows. Puede estar bloqueando la conexión de Python.")
else:
    print("\n✅ ¡Conexión exitosa con el stream de video!")
    ret, frame = cap.read()
    if ret:
        print(f"✅ ¡Frame capturado exitosamente! Dimensiones: {frame.shape}")
    else:
        print("🟡 Conexión exitosa, pero no se pudo leer el primer frame. El stream podría estar vacío.")

# Liberamos los recursos
cap.release()
print("\nScript finalizado.")