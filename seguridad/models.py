from django.db import models
from django.contrib.auth.models import User
from condominio.models import Propiedad


class Visitante(models.Model):
    nombre_completo = models.CharField(max_length=255)
    documento_identidad = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return f"{self.nombre_completo} ({self.documento_identidad})"


class Visita(models.Model):
    propiedad = models.ForeignKey(
        Propiedad, on_delete=models.CASCADE, related_name="visitas"
    )
    visitante = models.ForeignKey(
        Visitante, on_delete=models.CASCADE, related_name="visitas"
    )
    fecha_ingreso_programado = models.DateTimeField()
    fecha_salida_programada = models.DateTimeField()
    ingreso_real = models.DateTimeField(null=True, blank=True)
    salida_real = models.DateTimeField(null=True, blank=True)
    registrado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["-fecha_ingreso_programado", "-id"]

    def __str__(self) -> str:
        return f"Visita de {self.visitante} a casa {self.propiedad.numero_casa}"


class Vehiculo(models.Model):
    # Si es de un residente, 'visitante' será null y debe tener 'propiedad'
    propiedad = models.ForeignKey(
        Propiedad, on_delete=models.CASCADE, related_name="vehiculos", null=True, blank=True
    )
    # Si es de un visitante, 'propiedad' puede ir en la visita programada
    visitante = models.ForeignKey(
        Visitante, on_delete=models.CASCADE, related_name="vehiculos", null=True, blank=True
    )
    placa = models.CharField(max_length=20, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.placa} - {self.marca} {self.modelo}"
