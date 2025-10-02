from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
# --- CORRECCIÓN AQUÍ ---
# Añadimos 'Regla' a la lista de modelos importados.
from .models import Propiedad, AreaComun, Aviso, Regla, LecturaAviso 

@admin.register(Propiedad)
class PropiedadAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero_casa', 'propietario')
    search_fields = ('numero_casa', 'propietario__username')
    
    # --- CAMBIO FINAL ---
    # Reemplazamos 'raw_id_fields' por 'autocomplete_fields'.
    autocomplete_fields = ('propietario',)

    
@admin.register(AreaComun)
class AreaComunAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'capacidad', 'costo_reserva')
    search_fields = ('nombre',)

@admin.register(Aviso)
class AvisoAdmin(admin.ModelAdmin):
    list_display = (
        'titulo', 'dirigido_a', 'activo', 'fecha_publicacion', 
        'total_lecturas_display', 'porcentaje_lectura_display', 'ver_lecturas_link'
    )
    list_filter = ('dirigido_a', 'activo', 'fecha_publicacion')
    search_fields = ('titulo', 'contenido')
    readonly_fields = ('fecha_publicacion', 'estadisticas_display')
    
    fieldsets = (
        ('Información del Aviso', {
            'fields': ('titulo', 'contenido', 'dirigido_a', 'activo')
        }),
        ('Información de Publicación', {
            'fields': ('fecha_publicacion',),
            'classes': ('collapse',)
        }),
        ('Estadísticas de Lectura', {
            'fields': ('estadisticas_display',),
            'classes': ('collapse',)
        }),
    )
    
    def total_lecturas_display(self, obj):
        """Muestra el total de lecturas en la lista"""
        try:
            return obj.lecturas.count()
        except Exception as e:
            return 0
    total_lecturas_display.short_description = "Lecturas"
    
    def porcentaje_lectura_display(self, obj):
        """Muestra el porcentaje de lectura con color"""
        try:
            # Calcular manualmente para evitar errores
            total_lecturas = obj.lecturas.count()
            
            # Calcular residentes objetivo
            from usuarios.models import Residente
            if obj.dirigido_a == 'TODOS':
                total_objetivo = Residente.objects.count()
            elif obj.dirigido_a == 'PROPIETARIOS':
                total_objetivo = Residente.objects.filter(rol='propietario').count()
            elif obj.dirigido_a == 'INQUILINOS':
                total_objetivo = Residente.objects.filter(rol='inquilino').count()
            else:
                total_objetivo = 0
            
            if total_objetivo == 0:
                porcentaje = 0
            else:
                porcentaje = round((total_lecturas / total_objetivo) * 100, 2)
            
            if porcentaje >= 80:
                color = 'green'
            elif porcentaje >= 50:
                color = 'orange'
            else:
                color = 'red'
                
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
                color, porcentaje
            )
        except Exception as e:
            return format_html('<span style="color: red;">Error: {}</span>', str(e)[:20])
    porcentaje_lectura_display.short_description = "% Leído"
    
    def ver_lecturas_link(self, obj):
        """Link para ver las lecturas del aviso"""
        if obj.id:
            from django.urls import reverse
            url = reverse('admin:condominio_lecturaaviso_changelist')
            return format_html(
                '<a href="{}?aviso__id__exact={}" target="_blank">Ver lecturas ({})</a>',
                url, obj.id, obj.lecturas.count()
            )
        return "-"
    ver_lecturas_link.short_description = "Lecturas"
    
    def estadisticas_display(self, obj):
        """Muestra estadísticas detalladas en el detalle del aviso"""
        if not obj.id:
            return "Guarda el aviso primero para ver estadísticas"
        
        try:
            from usuarios.models import Residente
            
            # Calcular estadísticas manualmente
            total_lecturas = obj.lecturas.count()
            
            if obj.dirigido_a == 'TODOS':
                total_objetivo = Residente.objects.count()
                residentes_objetivo = Residente.objects.all()
            elif obj.dirigido_a == 'PROPIETARIOS':
                total_objetivo = Residente.objects.filter(rol='propietario').count()
                residentes_objetivo = Residente.objects.filter(rol='propietario')
            elif obj.dirigido_a == 'INQUILINOS':
                total_objetivo = Residente.objects.filter(rol='inquilino').count()
                residentes_objetivo = Residente.objects.filter(rol='inquilino')
            else:
                total_objetivo = 0
                residentes_objetivo = Residente.objects.none()
            
            porcentaje = round((total_lecturas / total_objetivo) * 100, 2) if total_objetivo > 0 else 0
            pendientes = total_objetivo - total_lecturas
            
            stats_html = f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h4>📊 Estadísticas de Lectura</h4>
                <ul style="margin: 0; padding-left: 20px;">
                    <li><strong>Dirigido a:</strong> {obj.get_dirigido_a_display()}</li>
                    <li><strong>Residentes objetivo:</strong> {total_objetivo}</li>
                    <li><strong>Total lecturas:</strong> {total_lecturas}</li>
                    <li><strong>Porcentaje leído:</strong> {porcentaje}%</li>
                    <li><strong>Pendientes:</strong> {pendientes}</li>
                </ul>
            </div>
            """
            
            # Agregar lista de residentes que leyeron
            if total_lecturas > 0:
                stats_html += """
                <div style="background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 10px 0;">
                    <h5>✅ Residentes que leyeron:</h5>
                    <ul style="margin: 0; padding-left: 20px;">
                """
                lecturas = obj.lecturas.select_related('residente__usuario')[:10]
                for lectura in lecturas:
                    stats_html += f"<li>{lectura.residente.usuario.username} - {lectura.fecha_lectura.strftime('%d/%m/%Y %H:%M')}</li>"
                
                if total_lecturas > 10:
                    stats_html += f"<li><em>... y {total_lecturas - 10} más</em></li>"
                
                stats_html += "</ul></div>"
            
            # Agregar residentes que NO han leído
            if pendientes > 0:
                stats_html += """
                <div style="background: #ffe8e8; padding: 15px; border-radius: 5px; margin: 10px 0;">
                    <h5>❌ Residentes que NO han leído:</h5>
                    <ul style="margin: 0; padding-left: 20px;">
                """
                residentes_que_leyeron = obj.lecturas.values_list('residente_id', flat=True)
                residentes_sin_leer = residentes_objetivo.exclude(id__in=residentes_que_leyeron)[:10]
                
                for residente in residentes_sin_leer:
                    stats_html += f"<li>{residente.usuario.username} ({residente.rol})</li>"
                
                if pendientes > 10:
                    stats_html += f"<li><em>... y {pendientes - 10} más</em></li>"
                
                stats_html += "</ul></div>"
            
            return mark_safe(stats_html)
            
        except Exception as e:
            return f"Error al cargar estadísticas: {str(e)}"
    
    estadisticas_display.short_description = "Estadísticas de Lectura"

@admin.register(LecturaAviso)
class LecturaAvisoAdmin(admin.ModelAdmin):
    list_display = (
        'get_aviso_titulo', 'get_residente_info', 'fecha_lectura', 'ip_lectura'
    )
    list_filter = (
        'fecha_lectura', 'aviso__dirigido_a'
    )
    search_fields = (
        'aviso__titulo', 'residente__usuario__username', 
        'residente__usuario__email'
    )
    readonly_fields = ('fecha_lectura',)
    
    def get_aviso_titulo(self, obj):
        """Muestra el título del aviso"""
        return obj.aviso.titulo[:50] + ('...' if len(obj.aviso.titulo) > 50 else '')
    get_aviso_titulo.short_description = "Aviso"
    
    def get_residente_info(self, obj):
        """Muestra información del residente"""
        return f"{obj.residente.usuario.username} ({obj.residente.rol})"
    get_residente_info.short_description = "Residente"
    
    def has_add_permission(self, request):
        """Las lecturas se crean automáticamente, no manualmente"""
        return False

@admin.register(Regla)
class ReglaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'activa')
    list_filter = ('categoria', 'activa')
    search_fields = ('titulo', 'descripcion', 'codigo')