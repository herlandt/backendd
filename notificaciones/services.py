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
