# En seguridad/services/detector.py

import cv2, numpy as np, time, io
from django.core.files.base import ContentFile
from .rekog import search_known_face, detect_faces
from seguridad.models import Camera, Deteccion
from django.contrib.auth import get_user_model

User = get_user_model()

def _encode_jpeg(frame_bgr):
    ok, buf = cv2.imencode(".jpg", frame_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    if not ok:
        return None
    return buf.tobytes()

def _user_from_match(match):
    ext = match["Face"].get("ExternalImageId")
    if not ext:
        return None
    try:
        return User.objects.filter(pk=int(ext)).first()
    except Exception:
        return User.objects.filter(username=ext).first()

# --- FUNCIÓN MODIFICADA ---
def run_detector(camera: Camera, fps=1, min_similarity=90.0, store_frames=True):
    """
    Bucle que toma N frames por segundo y busca rostros conocidos.
    Ahora con logs para depuración.
    """
    cap = cv2.VideoCapture(camera.rtsp_url, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        print(f"ERROR: No se pudo abrir el stream RTSP: {camera.rtsp_url}")
        raise RuntimeError(f"No puedo abrir RTSP: {camera.rtsp_url}")

    print("-> Stream de video abierto correctamente. Empezando bucle de detección...")
    interval = 1.0 / max(fps, 0.1)
    frame_count = 0
    try:
        while camera.active:
            t0 = time.time()
            ok, frame = cap.read()
            frame_count += 1

            if not ok or frame is None:
                print("ADVERTENCIA: No se pudo leer el frame del video. Reintentando...")
                time.sleep(0.5)
                continue

            # Solo procesamos según los FPS definidos
            if frame_count % (30 / fps) < 1: # Aproximación para video de 30fps
                print(f"\n--- Procesando Frame #{frame_count} ---")
                jpg = _encode_jpeg(frame)
                if not jpg:
                    print("ERROR: No se pudo codificar el frame a JPG.")
                    continue

                # 1. Llamada a AWS para detectar si hay caras
                print("-> Enviando a AWS para detectar caras...")
                det = detect_faces(jpg)

                if not det.get("FaceDetails"):
                    print("-> Resultado: No se detectaron caras en este frame.")
                    pass
                else:
                    print(f"-> Resultado: ¡Éxito! Se encontraron {len(det.get('FaceDetails'))} cara(s).")

                    # 2. Si hay caras, buscamos coincidencias
                    print("-> Buscando coincidencias en la colección...")
                    matches = search_known_face(jpg, threshold=min_similarity, max_faces=1)
                    matched_user = None
                    face_id = ""
                    similarity = None

                    if matches:
                        m = matches[0]
                        similarity = float(m.get("Similarity", 0))
                        face_id = m["Face"]["FaceId"]
                        matched_user = _user_from_match(m)
                        print(f"-> ¡COINCIDENCIA ENCONTRADA! Usuario: {matched_user}, Similitud: {similarity:.2f}%")
                    else:
                        print("-> No se encontraron coincidencias para las caras detectadas.")

                    # 3. Guardar el evento en la base de datos
                    ev = Deteccion(
                        camera=camera,
                        matched_user=matched_user,
                        face_id=face_id,
                        similarity=similarity,
                        raw={"det": det, "matches": matches}
                    )
                    if store_frames:
                        ev.frame.save("frame.jpg", ContentFile(jpg), save=False)
                    ev.save()
                    print("-> Registro de Deteccion guardado en la base de datos.")

            elapsed = time.time() - t0
            time.sleep(max(0, interval - elapsed))
    except Exception as e:
        print(f"ERROR INESPERADO EN EL BUCLE DEL DETECTOR: {e}")
    finally:
        print("-> Cerrando stream de video.")
        cap.release()



# Al final de seguridad/services/detector.py
from .rekog import detect_text # <-- Añade esta importación al inicio del archivo
from seguridad.models import EventoSeguridad, Vehiculo # <-- Añade esta importación también

# ... (el resto de las funciones existentes) ...

def run_plate_detector(camera: Camera, fps=1):
    """
    Bucle que toma N frames por segundo de una cámara y busca matrículas de vehículos.
    """
    cap = cv2.VideoCapture(camera.rtsp_url, cv2.CAP_FFMPG)
    if not cap.isOpened():
        print(f"ERROR: No se pudo abrir el stream RTSP: {camera.rtsp_url}")
        return

    print(f"-> Vigilando matrículas en la cámara: {camera.name} ({camera.rtsp_url})")
    interval = 1.0 / max(fps, 0.1)

    last_detected_plate = None
    last_detected_time = 0

    try:
        while camera.active:
            t0 = time.time()
            ok, frame = cap.read()
            if not ok or frame is None:
                time.sleep(0.5)
                continue

            jpg_data = _encode_jpeg(frame)
            if not jpg_data:
                continue

            # Detectar texto en el frame
            text_detections = detect_text(jpg_data)

            # Filtrar solo las matrículas (simplificado para placas de Bolivia: 1234ABC)
            for detection in text_detections:
                plate = detection.get("DetectedText", "").replace(" ", "").upper()
                # Lógica simple para evitar procesar la misma matrícula repetidamente
                if len(plate) > 4 and detection.get("Type") == "LINE":
                    if plate == last_detected_plate and (time.time() - last_detected_time) < 10:
                        continue

                    print(f"-> Matrícula detectada: {plate}")
                    last_detected_plate = plate
                    last_detected_time = time.time()

                    # Verificar si el vehículo está autorizado
                    vehiculo_autorizado = Vehiculo.objects.filter(placa=plate).first()

                    if vehiculo_autorizado:
                        print(f"  - ✅ Vehículo AUTORIZADO (Propiedad: {vehiculo_autorizado.propiedad})")
                        EventoSeguridad.objects.create(
                            tipo_evento=EventoSeguridad.ACCESO_VEHICULAR,
                            placa=plate,
                            autorizado=True,
                            motivo="Vehículo registrado"
                        )
                    else:
                        print(f"  - ❌ Vehículo DENEGADO")
                        EventoSeguridad.objects.create(
                            tipo_evento=EventoSeguridad.ACCESO_VEHICULAR,
                            placa=plate,
                            autorizado=False,
                            motivo="Vehículo no registrado"
                        )
                    # Aquí se podría añadir la lógica para enviar notificaciones push

            elapsed = time.time() - t0
            time.sleep(max(0, interval - elapsed))
    finally:
        print("-> Cerrando stream de cámara de matrículas.")
        cap.release()