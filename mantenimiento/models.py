from django.db import models
from django.contrib.auth import get_user_model
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

    propiedad = models.ForeignKey(
        Propiedad, on_delete=models.CASCADE, related_name="solicitudes_mantenimiento"
    )
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    solicitado_por = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="solicitudes_mantenimiento"
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

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"#{self.pk} - {self.titulo}"
