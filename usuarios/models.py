from django.db import models
from django.contrib.auth.models import User
# Importamos Propiedad desde la app 'condominio'
from condominio.models import Propiedad

class Residente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='residentes')
    ROL_CHOICES = (
        ('propietario', 'Propietario'),
        ('inquilino', 'Inquilino'),
        ('otro', 'Otro'),
    )
    rol = models.CharField(max_length=20, choices=ROL_CHOICES)
    fcm_token = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.propiedad}"