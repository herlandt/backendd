# En usuarios/models.py

from django.db import models
from django.contrib.auth.models import User

# NO importamos Propiedad directamente para evitar el ciclo.

class UserProfile(models.Model):
    class Role(models.TextChoices):
        PROPIETARIO = 'PROPIETARIO', 'Propietario (Admin)'
        RESIDENTE = 'RESIDENTE', 'Residente (Inquilino)'
        SEGURIDAD = 'SEGURIDAD', 'Personal de Seguridad'
        MANTENIMIENTO = 'MANTENIMIENTO', 'Personal de Mantenimiento'

    class Especialidad(models.TextChoices):
        ELECTRICIDAD = 'ELECTRICIDAD', 'Electricista'
        PLOMERIA = 'PLOMERIA', 'Plomero'
        JARDINERIA = 'JARDINERIA', 'Jardinería'
        PINTURA = 'PINTURA', 'Pintura'
        LIMPIEZA = 'LIMPIEZA', 'Limpieza'
        CARPINTERIA = 'CARPINTERIA', 'Carpintería'
        AIRES = 'AIRES', 'Aire Acondicionado'
        GENERAL = 'GENERAL', 'Mantenimiento General'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=50, choices=Role.choices, default=Role.RESIDENTE)
    especialidad = models.CharField(
        max_length=50, 
        choices=Especialidad.choices, 
        blank=True, 
        null=True,
        help_text="Especialidad (solo para personal de mantenimiento)"
    )

    def __str__(self):
        if self.role == self.Role.MANTENIMIENTO and self.especialidad:
            return f"{self.user.username} - {self.role} ({self.especialidad})"
        return f"{self.user.username} - {self.role}"

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