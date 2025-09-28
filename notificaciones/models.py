from django.db import models
from usuarios.models import User

class Dispositivo(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dispositivos')
    token_dispositivo = models.CharField(max_length=255, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Dispositivo"
        verbose_name_plural = "Dispositivos"

    def __str__(self):
        return f"Dispositivo de {self.usuario.username}"