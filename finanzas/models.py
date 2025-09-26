from decimal import Decimal
from django.db import models
from django.db.models import Sum
from django.contrib.auth import get_user_model
from condominio.models import Propiedad, AreaComun

User = get_user_model()


class Gasto(models.Model):
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='gastos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField(null=True, blank=True)
    descripcion = models.TextField(blank=True)
    pagado = models.BooleanField(default=False)

    # No forzamos unicidad por mes/año para permitir varios gastos en el mismo mes
    mes = models.PositiveSmallIntegerField()
    anio = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        # Completa mes/año a partir de fecha_emision si vienen vacíos
        if self.fecha_emision and (not self.mes or self.mes == 0):
            self.mes = self.fecha_emision.month
        if self.fecha_emision and (not self.anio or self.anio == 0):
            self.anio = self.fecha_emision.year
        super().save(*args, **kwargs)

    # --- Ayudantes útiles ---
    @property
    def total_pagado(self) -> Decimal:
        return self.pagos.aggregate(s=Sum('monto_pagado'))['s'] or Decimal('0')

    @property
    def saldo(self) -> Decimal:
        return (self.monto or Decimal('0')) - self.total_pagado

    def __str__(self):
        return f"Gasto #{self.pk} - Prop {self.propiedad_id} - {self.mes}/{self.anio}"


class Pago(models.Model):
    gasto = models.ForeignKey(Gasto, on_delete=models.CASCADE, related_name='pagos')
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='pagos',
                                null=True, blank=True)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(auto_now_add=True)
    comprobante = models.FileField(upload_to='comprobantes/', null=True, blank=True)

    def __str__(self):
        return f"Pago #{self.pk} -> Gasto {self.gasto_id} ({self.monto_pagado})"


class Reserva(models.Model):
    area_comun = models.ForeignKey(AreaComun, on_delete=models.CASCADE, related_name='reservas')
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='reservas')
    fecha_reserva = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pagada = models.BooleanField(default=False)

    def __str__(self):
        return f"Reserva {self.area_comun} {self.fecha_reserva} {self.hora_inicio}-{self.hora_fin}"
