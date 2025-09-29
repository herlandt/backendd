# en auditoria/models.py

from django.db import models
from django.conf import settings

class Bitacora(models.Model):
    """
    Modelo para registrar eventos importantes en el sistema.
    """
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Usuario"
    )
    ip_address = models.GenericIPAddressField(verbose_name="Dirección IP", null=True, blank=True)
    accion = models.CharField(max_length=255, verbose_name="Acción Realizada")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción Detallada")

    class Meta:
        verbose_name = "Registro de Bitácora"
        verbose_name_plural = "Registros de Bitácora"
        ordering = ['-timestamp']

    def __str__(self):
        user_info = self.usuario.username if self.usuario else "Sistema"
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] - {user_info} - {self.accion}"