# En usuarios/models.py

from django.db import models
from django.contrib.auth.models import User

# NO importamos Propiedad directamente para evitar el ciclo.

class Residente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    face_id_aws = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        unique=True,
        help_text="ID único del rostro asignado por AWS Rekognition."
    )
    # --- ESTA ES LA ÚNICA CORRECCIÓN REAL ---
    # Usamos una referencia en texto ('app.Modelo') que Django resuelve después.
    propiedad = models.ForeignKey(
        'condominio.Propiedad', 
        on_delete=models.CASCADE, 
        related_name='residentes',
        null=True,  # Permite que el campo esté vacío en la base de datos
        blank=True  # Permite que el campo esté vacío en los formularios del admin
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