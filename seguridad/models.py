from django.db import models
from django.utils import timezone
from condominio.models import Propiedad


class Visitante(models.Model):
    nombre_completo = models.CharField(max_length=255)
    documento = models.CharField(max_length=50, unique=True)
    telefono = models.CharField(max_length=30, blank=True, default="")
    email = models.EmailField(blank=True, default="")

    def __str__(self):
        return f"{self.nombre_completo} ({self.documento})"


class Vehiculo(models.Model):
    placa = models.CharField(max_length=20, unique=True)
    # Residente si tiene propiedad, visitante si tiene visitante.
    propiedad = models.ForeignKey(
        Propiedad, on_delete=models.CASCADE, null=True, blank=True,
        related_name="vehiculos"
    )
    visitante = models.ForeignKey(
        Visitante, on_delete=models.CASCADE, null=True, blank=True,
        related_name="vehiculos"
    )

    def __str__(self):
        return self.placa

    @property
    def es_residente(self) -> bool:
        return self.propiedad_id is not None


class Visita(models.Model):
    # Estados posibles para una visita
    class EstadoVisita(models.TextChoices):
        PROGRAMADA = 'PROGRAMADA', 'Programada'
        EN_CURSO = 'EN_CURSO', 'En Curso'
        FINALIZADA = 'FINALIZADA', 'Finalizada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    visitante = models.ForeignKey(Visitante, on_delete=models.CASCADE, related_name="visitas")
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name="visitas")

    fecha_ingreso_programado = models.DateTimeField()
    fecha_salida_programada = models.DateTimeField()

    ingreso_real = models.DateTimeField(null=True, blank=True)
    salida_real = models.DateTimeField(null=True, blank=True)
    
    # Campo estado agregado para solucionar error de filtros
    estado = models.CharField(
        max_length=20,
        choices=EstadoVisita.choices,
        default=EstadoVisita.PROGRAMADA,
        db_index=True
    )

    def save(self, *args, **kwargs):
        # Actualizar estado automáticamente basado en ingresos/salidas
        if self.ingreso_real and not self.salida_real:
            self.estado = self.EstadoVisita.EN_CURSO
        elif self.ingreso_real and self.salida_real:
            self.estado = self.EstadoVisita.FINALIZADA
        super().save(*args, **kwargs)

    class Meta:
        ordering = ("-fecha_ingreso_programado",)

    def __str__(self):
        return f"{self.visitante} → {self.propiedad} ({self.estado})"

# seguridad/models.py

# ... (tus otros modelos: Visitante, Vehiculo, Visita) ...

# ========= NUEVO MODELO PARA REGISTRO DE EVENTOS DE IA =========

class EventoSeguridad(models.Model):
    """
    Registra cada evento de acceso detectado por un sistema de IA,
    como una cámara de reconocimiento de matrículas.
    """
    class TipoEvento(models.TextChoices):
        INGRESO = 'INGRESO', 'Ingreso Vehicular'
        SALIDA = 'SALIDA', 'Salida Vehicular'

    class AccionTomada(models.TextChoices):
        PERMITIDO = 'PERMITIDO', 'Acceso Permitido'
        DENEGADO = 'DENEGADO', 'Acceso Denegado'

    fecha_hora = models.DateTimeField(auto_now_add=True)
    tipo_evento = models.CharField(max_length=10, choices=TipoEvento.choices)
    placa_detectada = models.CharField(max_length=20, help_text="La matrícula tal como fue detectada por la IA.")
    accion = models.CharField(max_length=10, choices=AccionTomada.choices)
    motivo = models.CharField(max_length=255, help_text="Razón por la que se tomó la acción (ej. 'Placa no encontrada').")
    vehiculo_registrado = models.ForeignKey(
        Vehiculo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Vehículo correspondiente en la base de datos, si existe."
    )

    class Meta:
        verbose_name = "Evento de Seguridad IA"
        verbose_name_plural = "Eventos de Seguridad IA"
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"[{self.fecha_hora.strftime('%Y-%m-%d %H:%M')}] {self.accion}: {self.placa_detectada}"
    
# seguridad/models.py  (o una app "vision")
from django.db import models
from django.conf import settings

class Camera(models.Model):
    name = models.CharField(max_length=50, unique=True)
    rtsp_url = models.CharField(max_length=500)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Deteccion(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name="detecciones")
    matched_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    face_id = models.CharField(max_length=100, blank=True, default="")
    similarity = models.FloatField(null=True, blank=True)  # 0..100
    ts = models.DateTimeField(auto_now_add=True)
    frame = models.ImageField(upload_to="detecciones/%Y/%m/%d/", blank=True)
    raw = models.JSONField(default=dict, blank=True)  # respuesta completa del proveedor

    class Meta:
        ordering = ["-ts"]
