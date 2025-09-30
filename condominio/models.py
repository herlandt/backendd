# En condominio/models.py

from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Propiedad(models.Model):
    numero_casa = models.CharField(max_length=10, unique=True)
    propietario = models.ForeignKey(User, on_delete=models.CASCADE) # <-- 2. Usa User
    metros_cuadrados = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"Casa N° {self.numero_casa}"

class AreaComun(models.Model):
    # ... (tu código de AreaComun aquí)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    capacidad = models.IntegerField()
    costo_reserva = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    horario_apertura = models.TimeField(null=True, blank=True)
    horario_cierre = models.TimeField(null=True, blank=True)
    
    def __str__(self):
        return self.nombre

class Aviso(models.Model):
    # ... (tu código de Aviso aquí)
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
        
class Regla(models.Model):
    # ... (tu código de Regla aquí)
    CATEGORIAS = [
        ('FINANZAS', 'Finanzas'),
        ('SEGURIDAD', 'Seguridad'),
        ('MANTENIMIENTO', 'Mantenimiento'),
        ('GENERAL', 'General'),
    ]
    codigo = models.CharField(max_length=50, unique=True, help_text="Un código único para la regla, ej: 'RESTRICCION_DEUDA_MANTENIMIENTO'")
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(help_text="La explicación detallada de la regla.")
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default='GENERAL')
    activa = models.BooleanField(default=True, help_text="Desmarcar para ocultar la regla sin borrarla.")

    def __str__(self):
        return self.titulo

class Reserva(models.Model):
    area_comun = models.ForeignKey('AreaComun', on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE) # <-- 3. Usa User también aquí
    fecha_reserva = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    ESTADOS = [
        ('SOLICITADA', 'Solicitada'),
        ('CONFIRMADA', 'Confirmada'),
        ('PAGADA', 'Pagada'),
        ('CANCELADA', 'Cancelada'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='SOLICITADA')
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reserva de {self.area_comun} por {self.usuario} el {self.fecha_reserva}"