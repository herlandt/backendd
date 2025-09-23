from django.db import models
from django.contrib.auth.models import User
from condominio.models import Propiedad

class PersonalMantenimiento(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_mantenimiento')
    especialidad = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.usuario.username} ({self.especialidad})"

class SolicitudMantenimiento(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completado', 'Completado'),
    )
    solicitado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='solicitudes_mantenimiento')
    propiedad = models.ForeignKey(Propiedad, on_delete=models.SET_NULL, null=True, related_name='solicitudes_mantenimiento')
    asignado_a = models.ForeignKey(PersonalMantenimiento, on_delete=models.SET_NULL, null=True, blank=True, related_name='tareas_asignadas')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        # Comprobamos si hay una propiedad antes de intentar mostrarla
        if self.propiedad:
            return f"{self.titulo} (Propiedad: {self.propiedad.numero_casa})"
        else:
            return f"{self.titulo} (Sin propiedad asignada)"