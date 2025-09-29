# auditoria/signals.py
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .services import registrar_evento

@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    ip = getattr(request, "ip_address", None)
    registrar_evento(user, ip, "Inicio de sesión", "Usuario inició sesión.")

@receiver(user_login_failed)
def on_login_failed(sender, credentials, request, **kwargs):
    ip = getattr(request, "ip_address", None)
    # Ojo: acá no hay user real todavía
    registrar_evento(None, ip, "Intento de inicio fallido", f"Credenciales: {credentials.get('username')}")

@receiver(user_logged_out)
def on_logout(sender, request, user, **kwargs):
    ip = getattr(request, "ip_address", None)
    registrar_evento(user, ip, "Cierre de sesión", "Usuario cerró sesión.")
