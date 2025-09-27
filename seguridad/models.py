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
