from .models import DeviceToken

def send_push(tokens, title, body, data=None):
    # Aquí integrarías FCM/APNs. Por ahora, simulamos envío:
    return {"sent": len(tokens), "note": "fake"}

def notificar_usuario(user, title, body, data=None):
    tokens = list(
        DeviceToken.objects.filter(user=user, active=True).values_list("token", flat=True)
    )
    if not tokens:
        return {"sent": 0, "note": "sin tokens"}
    return send_push(tokens, title, body, data or {})
