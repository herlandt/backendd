# usuarios/models.py (Corregido)
from django.db import models
from django.contrib.auth.models import User

# Se elimina la importación directa de 'Propiedad' para romper el ciclo.
# from condominio.models import Propiedad

class Residente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    # --- CORRECCIÓN AQUÍ ---
    # Se usa una referencia en formato de texto 'app.Modelo'.
    # Django resolverá esta relación sin necesidad de importar el modelo directamente.
    propiedad = models.ForeignKey('condominio.Propiedad', on_delete=models.CASCADE, related_name='residentes')
    ROL_CHOICES = (
        ('propietario', 'Propietario'),
        ('inquilino', 'Inquilino'),
        ('otro', 'Otro'),
    )
    rol = models.CharField(max_length=20, choices=ROL_CHOICES)
    fcm_token = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        # Es más seguro verificar si la propiedad existe antes de imprimirla
        if hasattr(self, 'propiedad') and self.propiedad:
            return f"{self.usuario.username} - {self.propiedad}"
        return self.usuario.username