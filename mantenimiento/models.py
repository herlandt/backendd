from django.db import models
from django.contrib.auth.models import User
from condominio.models import Propiedad
from usuarios.models import Residente # <-- Importamos Residente que sí existe

# Se define el modelo de Personal de Mantenimiento aquí mismo
class PersonalMantenimiento(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_mantenimiento')
    especialidad = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.usuario.username} ({self.especialidad})"

class SolicitudMantenimiento(models.Model):
    ESTADO_OPCIONES = ( # Cambié el nombre a ESTADO_OPCIONES para que coincida con el código que te di antes
        ('Pendiente', 'Pendiente'),
        ('En Proceso', 'En Proceso'),
        ('Completado', 'Completado'),
        ('Cancelado', 'Cancelado'),
    )
    # La solicitud la hace un Residente, no un User genérico
    solicitado_por = models.ForeignKey(Residente, on_delete=models.CASCADE, related_name='solicitudes_mantenimiento')
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='solicitudes_mantenimiento')
    # La FK apunta a PersonalMantenimiento, que está definido arriba
    asignado_a = models.ForeignKey(PersonalMantenimiento, on_delete=models.SET_NULL, null=True, blank=True, related_name='tareas_asignadas')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_OPCIONES, default='Pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.propiedad:
            return f"{self.titulo} (Propiedad: {self.propiedad.numero_casa})"
        else:
            return f"{self.titulo} (Sin propiedad asignada)"