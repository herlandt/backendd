from django.db import models
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
    visitante = models.ForeignKey(Visitante, on_delete=models.CASCADE, related_name="visitas")
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name="visitas")

    fecha_ingreso_programado = models.DateTimeField()
    fecha_salida_programada = models.DateTimeField()

    ingreso_real = models.DateTimeField(null=True, blank=True)
    salida_real = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-fecha_ingreso_programado",)

    def __str__(self):
        return f"{self.visitante} → {self.propiedad}"

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