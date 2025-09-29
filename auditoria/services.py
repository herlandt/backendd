# en auditoria/services.py

from .models import Bitacora

def registrar_evento(usuario, ip_address, accion, descripcion=""):
    """
    Crea un nuevo registro en la Bitácora.
    """
    Bitacora.objects.create(
        usuario=usuario,
        ip_address=ip_address,
        accion=accion,
        descripcion=descripcion
    )