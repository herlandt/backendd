from django.db import models
from django.contrib.auth.models import User
from condominio.models import Propiedad, AreaComun

class Gasto(models.Model):
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='gastos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_emision = models.DateField(auto_now_add=True)
    fecha_vencimiento = models.DateField()
    descripcion = models.CharField(max_length=255)
    pagado = models.BooleanField(default=False)
    def __str__(self):
        return f"Gasto de {self.monto} para {self.propiedad} (Vence: {self.fecha_vencimiento})"

class Pago(models.Model):
    gasto = models.ForeignKey(Gasto, on_delete=models.CASCADE, related_name='pagos')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pagos')
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    comprobante = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return f"Pago de {self.monto_pagado} por {self.usuario.username} el {self.fecha_pago}"

class Reserva(models.Model):
    area_comun = models.ForeignKey(AreaComun, on_delete=models.CASCADE, related_name='reservas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservas')
    fecha_reserva = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    costo_total = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    pagada = models.BooleanField(default=False)
    def __str__(self):
        return f"Reserva de {self.area_comun.nombre} por {self.usuario.username} para el {self.fecha_reserva}"