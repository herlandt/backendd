# En usuarios/models.py

from django.db import models
from django.contrib.auth.models import User

# NO importamos Propiedad directamente para evitar el ciclo.

class Residente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # --- ESTA ES LA ÚNICA CORRECCIÓN REAL ---
    # Usamos una referencia en texto ('app.Modelo') que Django resuelve después.
    propiedad = models.ForeignKey(
        'condominio.Propiedad', 
        on_delete=models.CASCADE, 
        related_name='residentes'
    )
    
    ROL_CHOICES = (
        ('propietario', 'Propietario'),
        ('inquilino', 'Inquilino'),
        ('otro', 'Otro'),
    )
    rol = models.CharField(max_length=20, choices=ROL_CHOICES)
    fcm_token = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        if hasattr(self, 'propiedad') and self.propiedad:
            return f"{self.usuario.username} - {self.propiedad}"
        return self.usuario.username