from django.db import models
from django.contrib.auth.models import User
from condominio.models import Propiedad, AreaComun
from django.db.models.signals import post_save
from django.db.models import Sum
from django.dispatch import receiver

# ===================================================================
# 1. MODELOS PRINCIPALES (los que se pagan)
#    Definimos Gasto, Multa y Reserva primero.
# ===================================================================

class Gasto(models.Model):
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='gastos')
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
        return f"Gasto {self.propiedad} {self.mes}/{self.anio} - {self.monto}"


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
    creado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='multas_creadas', null=True, blank=True)

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

# ===================================================================
# 2. MODELOS DE PAGO (los que referencian a los anteriores)
#    Definimos Pago y PagoMulta al final.
# ===================================================================



class Pago(models.Model):
    # ... (todos tus campos existentes)
    gasto = models.ForeignKey(Gasto, on_delete=models.CASCADE, related_name='pagos', null=True, blank=True)
    multa = models.ForeignKey(Multa, on_delete=models.CASCADE, related_name='pagos', null=True, blank=True)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='pagos', null=True, blank=True)
    usuario = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='pagos'
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
        # ... (tu método __str__)
        if self.gasto:
            return f"Pago {self.monto_pagado} de {self.gasto}"
        elif self.multa:
            return f"Pago {self.monto_pagado} de {self.multa}"
        elif self.reserva:
            return f"Pago {self.monto_pagado} de {self.reserva}"
        return f"Pago {self.id} por {self.monto_pagado}"

    # --- AÑADE ESTE MÉTODO ---
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) # Guarda el pago primero
        # Ahora, actualiza el estado del gasto asociado
        if self.gasto:
            total_pagado = self.gasto.pagos.aggregate(total=Sum('monto_pagado'))['total'] or 0
            if total_pagado >= self.gasto.monto:
                self.gasto.pagado = True
            else:
                self.gasto.pagado = False
            self.gasto.save()

# ... (el resto de tus modelos)


class PagoMulta(models.Model):
    multa = models.ForeignKey(Multa, on_delete=models.CASCADE, related_name='pagos_multa')
    usuario = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='pagos_multas',
        null=True, blank=True
    )
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(auto_now_add=True)
    comprobante = models.FileField(upload_to='comprobantes_multas/', null=True, blank=True)

    def __str__(self):
        return f"PagoMulta {self.monto_pagado} de {self.multa}"
    


class Egreso(models.Model):
    """
    Representa las salidas de dinero del condominio.
    """
    CATEGORIA_CHOICES = [
        ('MANTENIMIENTO', 'Mantenimiento y Reparaciones'),
        ('SERVICIOS', 'Servicios Públicos (Agua, Luz)'),
        ('SUELDOS', 'Sueldos y Salarios'),
        ('ADMIN', 'Gastos Administrativos'),
        ('LIMPIEZA', 'Limpieza y Jardinería'),
        ('SEGURIDAD', 'Seguridad'),
        ('OTROS', 'Otros'),
    ]

    fecha = models.DateField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    concepto = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    comprobante = models.FileField(upload_to='comprobantes_egresos/', blank=True, null=True)
    solicitud_mantenimiento = models.ForeignKey(
        'mantenimiento.SolicitudMantenimiento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='egresos'
    )

    class Meta:
        verbose_name = "Egreso"
        verbose_name_plural = "Egresos"
        ordering = ['-fecha']

    def __str__(self):
        return f"Egreso: {self.concepto} - ${self.monto}"


class Ingreso(models.Model):
    """
    Representa las entradas de dinero al condominio,
    especialmente las que se registran manualmente.
    """
    fecha = models.DateField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    concepto = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    pago_relacionado = models.OneToOneField(
        Pago,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ingreso_manual'
    )

    class Meta:
        verbose_name = "Ingreso"
        verbose_name_plural = "Ingresos"
        ordering = ['-fecha']

    def __str__(self):
        return f"Ingreso: {self.concepto} - ${self.monto}"


# ========= SIGNALS PARA INGRESOS AUTOMÁTICOS =========
# en finanzas/models.py

# ... (todo tu código anterior se mantiene igual) ...


# ========= SIGNALS PARA INGRESOS AUTOMÁTICOS (VERSIÓN FINAL) =========

@receiver(post_save, sender=Pago)
def crear_ingreso_desde_pago(sender, instance, created, **kwargs):
    """
    Crea un registro de Ingreso automáticamente cuando un Pago se marca como completado.
    """
    if instance.estado_pago == 'completado' and not hasattr(instance, 'ingreso_manual'):
        concepto = "Ingreso no especificado"
        if instance.gasto:
            concepto = f"Pago de expensa: {instance.gasto.descripcion}"
        elif instance.multa:
            # Asumiendo que el modelo Multa tiene un campo 'motivo' o 'concepto'
            concepto = f"Pago de multa: {getattr(instance.multa, 'motivo', instance.multa.concepto)}"
        elif instance.reserva:
            concepto = f"Pago de reserva: {instance.reserva.area_comun.nombre}"

        Ingreso.objects.get_or_create(
            pago_relacionado=instance,
            defaults={
                'fecha': instance.fecha_pago,
                'monto': instance.monto_pagado,  # <--- ¡CORREGIDO! (con guion bajo)
                'concepto': concepto,
                'descripcion': f"Ingreso automático generado desde el pago ID {instance.id}"
            }
        )