from django.db import models
from django.contrib.auth.models import User

class Propiedad(models.Model):
    numero_casa = models.CharField(max_length=10, unique=True)
    propietario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='propiedades')
    metros_cuadrados = models.DecimalField(max_digits=8, decimal_places=2)
    def __str__(self):
        return f"Casa N° {self.numero_casa}"

class AreaComun(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    capacidad = models.IntegerField()
    costo_reserva = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    horario_apertura = models.TimeField(null=True, blank=True)
    horario_cierre = models.TimeField(null=True, blank=True)
    def __str__(self):
        return self.nombre
    
class Aviso(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo