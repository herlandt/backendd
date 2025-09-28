# En usuarios/models.py

from django.contrib.auth.models import AbstractUser,Group, Permission
from django.db import models

class Usuario(AbstractUser):
    # AbstractUser ya incluye: username, password, email, first_name, last_name.
    # Puedes añadir campos extra si los necesitas en el futuro.
    pass
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="usuario_set", # Nombre único para la relación inversa
        related_query_name="usuario",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="usuario_set", # Nombre único para la relación inversa
        related_query_name="usuario",
    )
 # Por ahora lo dejamos así para no añadir campos extra.

class Residente(models.Model):
    # Aquí vinculas tu modelo Residente con el nuevo modelo Usuario
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
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