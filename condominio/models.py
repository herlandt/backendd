# condominio/models.py (Corregido)
from django.db import models
from django.conf import settings # Se importa settings

# Se eliminan las importaciones problemáticas que causaban el ciclo.

class Propiedad(models.Model):
    numero_casa = models.CharField(max_length=10, unique=True)
    # --- CORRECCIÓN AQUÍ ---
    # Se usa la referencia de Django al modelo de usuario activo.
    # Esto rompe la dependencia directa y soluciona el ciclo de importación.
    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='propiedades'
    )
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

class Regla(models.Model):
    """
    Almacena una regla de negocio del condominio para ser mostrada en el frontend.
    """
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

    class Meta:
        verbose_name = "Regla del Condominio"
        verbose_name_plural = "Reglas del Condominio"
        ordering = ['categoria', 'titulo']

    def __str__(self):
        return self.titulo