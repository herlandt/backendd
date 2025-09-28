from django.contrib import admin
# --- CORRECCIÓN AQUÍ ---
# Añadimos 'Regla' a la lista de modelos importados.
from .models import Propiedad, AreaComun, Aviso, Regla 

@admin.register(Propiedad)
class PropiedadAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero_casa', 'propietario')
    search_fields = ('numero_casa', 'propietario__username')
    
    # 2. ESTA ES LA LÍNEA MÁGICA:
    # Cambia el campo de texto por una ventana de búsqueda que SÍ funciona.
    raw_id_fields = ('propietario',)


    
@admin.register(AreaComun)
class AreaComunAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'capacidad', 'costo_reserva')
    search_fields = ('nombre',)

@admin.register(Aviso)
class AvisoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_publicacion')
    search_fields = ('titulo', 'contenido')

@admin.register(Regla)
class ReglaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'activa')
    list_filter = ('categoria', 'activa')
    search_fields = ('titulo', 'descripcion', 'codigo')