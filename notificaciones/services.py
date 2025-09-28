import json
import logging
import requests
from django.conf import settings

log = logging.getLogger(__name__)

def send_push(tokens, title, body, data=None):
    """
    Envío real con FCM si hay credenciales; si no, modo simulación (log + OK).
    Config opcional:
      - FCM_SERVER_KEY (legacy)  O  NOTIF_FAKE_SEND=true para simular
    """
    data = data or {}

    # Simulación si no hay clave
    server_key = getattr(settings, "FCM_SERVER_KEY", None)
    fake = getattr(settings, "NOTIF_FAKE_SEND", False)
    if not server_key or fake:
        log.info("[PUSH-FAKE] title=%s body=%s tokens=%d data=%s", title, body, len(tokens), json.dumps(data))
        return {"sent": len(tokens), "mode": "fake"}

    # Envío FCM (legacy)
    url = "https://fcm.googleapis.com/fcm/send"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"key={server_key}",
    }
    payload = {
        "registration_ids": list(tokens),
        "notification": {"title": title, "body": body},
        "data": data,
        "android": {"priority": "high"},
    }
    try:
        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
        resp.raise_for_status()
        res = resp.json()
        return {"sent": res.get("success", 0), "mode": "fcm", "raw": res}
    except Exception as e:
        log.exception("Error enviando push: %s", e)
        return {"sent": 0, "mode": "error", "error": str(e)}


# notificaciones/services.py

import requests
from django.conf import settings
from .models import Dispositivo

def notificar_usuario(usuario, titulo, cuerpo):
    """
    Busca todos los dispositivos de un usuario y les envía una notificación push.
    """
    # Buscamos todos los tokens de los dispositivos registrados para ese usuario
    dispositivos = Dispositivo.objects.filter(usuario=usuario, activo=True)
    tokens = [d.token_dispositivo for d in dispositivos]

    if not tokens:
        print(f"INFO: El usuario {usuario.username} no tiene dispositivos activos para notificar.")
        return

    # Si estamos en modo de prueba (NOTIF_FAKE_SEND=True en settings.py),
    # solo imprimimos en la consola en lugar de enviar una notificación real.
    if getattr(settings, 'NOTIF_FAKE_SEND', False):
        print("--- SIMULACIÓN DE NOTIFICACIÓN PUSH ---")
        print(f"Para: {usuario.username}")
        print(f"Tokens: {tokens}")
        print(f"Título: {titulo}")
        print(f"Cuerpo: {cuerpo}")
        print("---------------------------------------")
        return

    # --- Lógica para enviar la notificación real con Firebase (FCM) ---
    headers = {
        'Authorization': f'key={settings.FCM_SERVER_KEY}',
        'Content-Type': 'application/json',
    }
    
    payload = {
        'registration_ids': tokens,  # Se pueden enviar a múltiples dispositivos a la vez
        'notification': {
            'title': titulo,
            'body': cuerpo,
        },
        'data': {
            # Aquí puedes añadir datos adicionales si tu app móvil los necesita
            'extra_info': 'Puedes agregar JSON aquí'
        }
    }

    try:
        response = requests.post('https://fcm.googleapis.com/fcm/send', headers=headers, json=payload)
        response.raise_for_status()  # Lanza un error si la petición falla (ej. 401, 500)
        print(f"Notificación enviada exitosamente a los dispositivos de {usuario.username}.")
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Falló el envío de notificación a FCM: {e}")