from django.contrib import admin
from .models import Propiedad, AreaComun
from .models import Propiedad, AreaComun, Aviso 
from django.contrib import admin
from .models import Propiedad, AreaComun, Aviso

@admin.register(Propiedad)
class PropiedadAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero_casa', 'propietario', 'metros_cuadrados')
    search_fields = ('numero_casa', 'propietario__username') 
admin.site.register(Aviso)
@admin.register(AreaComun)
class AreaComunAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'capacidad', 'costo_reserva', 'horario_apertura', 'horario_cierre')
    list_editable = ('costo_reserva', 'horario_apertura', 'horario_cierre')

@admin.register(Regla)
class ReglaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'activa')
    list_filter = ('categoria', 'activa')
    search_fields = ('titulo', 'descripcion', 'codigo')