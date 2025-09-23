from django.db import models
from django.contrib.auth.models import User
from condominio.models import Propiedad

class Visitante(models.Model):
    nombre_completo = models.CharField(max_length=255)
    documento_identidad = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.nombre_completo

class Visita(models.Model):
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='visitas')
    visitante = models.ForeignKey(Visitante, on_delete=models.CASCADE, related_name='visitas')
    fecha_ingreso_programado = models.DateTimeField()
    fecha_salida_programada = models.DateTimeField()
    ingreso_real = models.DateTimeField(null=True, blank=True)
    salida_real = models.DateTimeField(null=True, blank=True)
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return f"{self.visitante.nombre_completo} a {self.propiedad.numero_casa}"

class Vehiculo(models.Model):
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='vehiculos', null=True, blank=True)
    visitante = models.ForeignKey(Visitante, on_delete=models.CASCADE, related_name='vehiculos', null=True, blank=True)
    placa = models.CharField(max_length=20, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.placa} ({self.marca} {self.modelo})"