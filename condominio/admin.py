from django.contrib import admin
from .models import Propiedad, AreaComun
from .models import Propiedad, AreaComun, Aviso 
admin.site.register(Propiedad)
admin.site.register(Aviso)
@admin.register(AreaComun)
class AreaComunAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'capacidad', 'costo_reserva', 'horario_apertura', 'horario_cierre')
    list_editable = ('costo_reserva', 'horario_apertura', 'horario_cierre')