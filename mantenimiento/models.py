from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from condominio.models import Propiedad

User = get_user_model()


class PersonalMantenimiento(models.Model):
    nombre = models.CharField(max_length=120)
    telefono = models.CharField(max_length=30, blank=True)
    especialidad = models.CharField(max_length=120, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class SolicitudMantenimiento(models.Model):
    ESTADO_PENDIENTE = "PENDIENTE"
    ESTADO_EN_PROGRESO = "EN_PROGRESO"
    ESTADO_FINALIZADA = "FINALIZADA"
    ESTADO_CANCELADA = "CANCELADA"
    ESTADOS = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_EN_PROGRESO, "En progreso"),
        (ESTADO_FINALIZADA, "Finalizada"),
        (ESTADO_CANCELADA, "Cancelada"),
    ]

    # Prioridades posibles para una solicitud
    class Prioridad(models.TextChoices):
        BAJA = 'BAJA', 'Baja'
        MEDIA = 'MEDIA', 'Media'
        ALTA = 'ALTA', 'Alta'
        URGENTE = 'URGENTE', 'Urgente'

    propiedad = models.ForeignKey(
        Propiedad, on_delete=models.CASCADE, related_name="solicitudes_mantenimiento"
    )
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    solicitado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,   # o PROTECT si así lo prefieres
        null=True,                   #  <- importante
        blank=True,                  #  <- importante
        related_name='solicitudes_mantenimiento',
    )
    asignado_a = models.ForeignKey(
        PersonalMantenimiento,
        on_delete=models.SET_NULL,
        related_name="trabajos",
        null=True,
        blank=True,
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_PENDIENTE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Campos agregados para solucionar errores de filtros
    prioridad = models.CharField(
        max_length=20, 
        choices=Prioridad.choices, 
        default=Prioridad.MEDIA,
        db_index=True
    )
    fecha_resolucion = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Fecha cuando se resolvió la solicitud"
    )

    def save(self, *args, **kwargs):
        # Asignar fecha de resolución automáticamente al completar
        if self.estado == self.ESTADO_FINALIZADA and not self.fecha_resolucion:
            self.fecha_resolucion = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"#{self.pk} - {self.titulo} (Prioridad: {self.prioridad})"
