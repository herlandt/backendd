# seguridad/services/detector.py
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
    """
    Si en tu indexado guardaste ExternalImageId con el username o el user_id,
    aquí puedes mapear al usuario.
    """
    ext = match["Face"].get("ExternalImageId")
    if not ext:
        return None
    # ejemplo: guardaste user_id como ExternalImageId
    try:
        return User.objects.filter(pk=int(ext)).first()
    except Exception:
        return User.objects.filter(username=ext).first()

def run_detector(camera: Camera, fps=1, min_similarity=90.0, store_frames=True):
    """
    Bucle simple que toma N frames por segundo y busca rostros conocidos.
    Llama a Rekognition para cada frame muestreado.
    """
    cap = cv2.VideoCapture(camera.rtsp_url, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        raise RuntimeError(f"No puedo abrir RTSP: {camera.rtsp_url}")

    interval = 1.0 / max(fps, 0.1)
    try:
        while camera.active:
            t0 = time.time()
            ok, frame = cap.read()
            if not ok or frame is None:
                time.sleep(0.5)
                continue

            jpg = _encode_jpeg(frame)
            if not jpg:
                continue

            # 1) primero verifica si hay rostros y luego intenta identificar
            det = detect_faces(jpg)
            if not det.get("FaceDetails"):
                # sin rostros -> salta
                pass
            else:
                matches = search_known_face(jpg, threshold=min_similarity, max_faces=1)
                matched_user = None
                face_id = ""
                similarity = None

                if matches:
                    m = matches[0]
                    similarity = float(m.get("Similarity", 0))
                    face_id = m["Face"]["FaceId"]
                    matched_user = _user_from_match(m)

                # guarda evento
                ev = Deteccion(camera=camera, matched_user=matched_user,
                               face_id=face_id, similarity=similarity, raw={"det": det, "matches": matches})
                if store_frames:
                    ev.frame.save("frame.jpg", ContentFile(jpg), save=False)
                ev.save()

            # espera para respetar el FPS
            elapsed = time.time() - t0
            time.sleep(max(0, interval - elapsed))
    finally:
        cap.release()
