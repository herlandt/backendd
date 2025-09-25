# finanzas/models.py
from django.db import models
from django.contrib.auth.models import User
from condominio.models import Propiedad, AreaComun
from usuarios.models import Residente

class Gasto(models.Model):
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='gastos')
    mes = models.IntegerField()
    anio = models.IntegerField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.CharField(max_length=255)
    fecha_emision = models.DateField(auto_now_add=True)
    fecha_vencimiento = models.DateField()
    pagado = models.BooleanField(default=False)

    class Meta:
        unique_together = ('propiedad', 'mes', 'anio')

    def __str__(self):
        return f"Gasto para {self.propiedad} - {self.mes}/{self.anio}"

class Pago(models.Model):
    residente = models.ForeignKey(Residente, on_delete=models.CASCADE, related_name='pagos')
    gasto = models.ForeignKey(Gasto, on_delete=models.CASCADE, related_name='pagos', null=True, blank=True)
    reserva = models.ForeignKey('Reserva', on_delete=models.SET_NULL, related_name='pagos', null=True, blank=True)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    
    METODO_PAGO = [
        ('transferencia', 'Transferencia Bancaria'),
        ('efectivo', 'Efectivo'),
    ]
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO)
    comprobante = models.FileField(upload_to='comprobantes/', blank=True, null=True)

    def __str__(self):
        return f"Pago de {self.residente.usuario.username} por {self.monto_pagado}"

class Reserva(models.Model):
    area_comun = models.ForeignKey(AreaComun, on_delete=models.CASCADE, related_name='reservas')
    residente = models.ForeignKey(Residente, on_delete=models.CASCADE, related_name='reservas')
    fecha_reserva = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    costo_total = models.DecimalField(max_digits=8, decimal_places=2)
    pagada = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Reserva de {self.area_comun.nombre} por {self.residente.usuario.username} el {self.fecha_reserva}"