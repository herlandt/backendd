from django.db import models
from django.contrib.auth import get_user_model
from condominio.models import Propiedad, AreaComun  # ajusta si el nombre difiere

User = get_user_model()


class Gasto(models.Model):
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='gastos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    # usamos fecha_emision como la “fecha” principal del gasto
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField(null=True, blank=True)

    descripcion = models.TextField(blank=True)
    pagado = models.BooleanField(default=False)

    # mes/año se guardan para facilitar filtros; se rellenan automáticamente
    mes = models.PositiveSmallIntegerField()
    anio = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        # completa mes/año desde fecha_emision si faltan
        if self.fecha_emision and not self.mes:
            self.mes = self.fecha_emision.month
        if self.fecha_emision and not self.anio:
            self.anio = self.fecha_emision.year
        super().save(*args, **kwargs)

    class Meta:
        # Permitimos varios gastos por (propiedad, mes, anio)
        # por eso NO definimos unique_together aquí.
        ordering = ('-anio', '-mes', 'propiedad_id')

    def __str__(self):
        return f"Gasto {self.propiedad} {self.mes}/{self.anio} - {self.monto}"


class Pago(models.Model):
    # Pago de GASTO
    gasto = models.ForeignKey(Gasto, on_delete=models.CASCADE, related_name='pagos', null=True, blank=True)
    multa = models.ForeignKey(Multa, on_delete=models.CASCADE, related_name='pagos', null=True, blank=True)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='pagos', null=True, blank=True)
    usuario = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='pagos',
       # null=True, blank=True
    )
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(auto_now_add=True)
    comprobante = models.FileField(upload_to='comprobantes/', null=True, blank=True)
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('FALLIDO', 'Fallido'),
    ]
    estado_pago = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    id_transaccion_pasarela = models.CharField(max_length=255, blank=True, null=True, unique=True)
    qr_data = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"Pago {self.monto_pagado} de {self.gasto}"


# --------- MULTAS ---------
class Multa(models.Model):
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='multas')
    concepto = models.CharField(max_length=255, default='General', blank=True) 
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField(null=True, blank=True)

    descripcion = models.TextField(blank=True)
    pagado = models.BooleanField(default=False)

    mes = models.PositiveSmallIntegerField()
    anio = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        if self.fecha_emision and not self.mes:
            self.mes = self.fecha_emision.month
        if self.fecha_emision and not self.anio:
            self.anio = self.fecha_emision.year
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('-anio', '-mes', 'propiedad_id')

    def __str__(self):
        return f"Multa {self.propiedad} {self.concepto} {self.mes}/{self.anio} - {self.monto}"


class PagoMulta(models.Model):
    # Pago de MULTA
    multa = models.ForeignKey(Multa, on_delete=models.CASCADE, related_name='pagos')
    usuario = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='pagos_multas',
        null=True, blank=True
    )
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(auto_now_add=True)
    comprobante = models.FileField(upload_to='comprobantes_multas/', null=True, blank=True)

    def __str__(self):
        return f"PagoMulta {self.monto_pagado} de {self.multa}"


# --------- RESERVAS ---------
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
