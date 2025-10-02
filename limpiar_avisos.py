import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from condominio.models import Aviso, LecturaAviso
from django.db.models import Count

def limpiar_avisos_duplicados():
    """Limpia avisos duplicados y sus lecturas"""
    
    print("🧹 LIMPIEZA DE AVISOS DUPLICADOS")
    print("=" * 40)
    
    # 1. Mostrar avisos actuales
    print("\n📋 Avisos actuales:")
    avisos = Aviso.objects.all().order_by('titulo', '-fecha_publicacion')
    
    for aviso in avisos:
        lecturas_count = aviso.lecturas.count()
        print(f"   - ID {aviso.id}: {aviso.titulo} ({aviso.fecha_publicacion.strftime('%d/%m/%Y %H:%M')}) - {lecturas_count} lecturas")
    
    # 2. Encontrar duplicados por título
    print(f"\n🔍 Buscando duplicados...")
    
    duplicados = Aviso.objects.values('titulo').annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    avisos_para_eliminar = []
    
    for dup in duplicados:
        titulo = dup['titulo']
        print(f"\n⚠️  Título duplicado: '{titulo}' ({dup['count']} veces)")
        
        # Obtener todas las versiones de este título
        versiones = Aviso.objects.filter(titulo=titulo).order_by('-fecha_publicacion')
        
        # Mantener solo la más reciente, marcar el resto para eliminación
        mas_reciente = versiones.first()
        print(f"   ✅ Mantener: ID {mas_reciente.id} ({mas_reciente.fecha_publicacion.strftime('%d/%m/%Y %H:%M')})")
        
        for version in versiones[1:]:  # Todas excepto la primera (más reciente)
            avisos_para_eliminar.append(version)
            print(f"   ❌ Eliminar: ID {version.id} ({version.fecha_publicacion.strftime('%d/%m/%Y %H:%M')})")
    
    # 3. Eliminar duplicados
    if avisos_para_eliminar:
        print(f"\n🗑️  Eliminando {len(avisos_para_eliminar)} avisos duplicados...")
        
        for aviso in avisos_para_eliminar:
            lecturas_count = aviso.lecturas.count()
            print(f"   🗑️  Eliminando aviso ID {aviso.id} y sus {lecturas_count} lecturas")
            aviso.delete()  # Esto también elimina las lecturas relacionadas
        
        print("   ✅ Limpieza completada")
    else:
        print("   ✅ No se encontraron duplicados")
    
    # 4. Mostrar estado final
    print(f"\n📊 ESTADO FINAL:")
    avisos_finales = Aviso.objects.all().order_by('-fecha_publicacion')
    total_lecturas = LecturaAviso.objects.count()
    
    print(f"   📋 Total avisos: {avisos_finales.count()}")
    print(f"   📖 Total lecturas: {total_lecturas}")
    
    for aviso in avisos_finales:
        lecturas_count = aviso.lecturas.count()
        print(f"   - {aviso.titulo}: {lecturas_count} lecturas")

def verificar_admin():
    """Verifica que el admin funcione correctamente"""
    
    print(f"\n🛡️  VERIFICACIÓN DEL PANEL ADMIN:")
    print("-" * 30)
    
    try:
        avisos = Aviso.objects.all()
        
        for aviso in avisos:
            print(f"\n🔹 {aviso.titulo}")
            
            # Probar los métodos del admin manualmente
            try:
                total_lecturas = aviso.lecturas.count()
                print(f"   ✅ Total lecturas: {total_lecturas}")
            except Exception as e:
                print(f"   ❌ Error en total_lecturas: {e}")
            
            try:
                # Calcular porcentaje manualmente como en el admin
                from usuarios.models import Residente
                
                if aviso.dirigido_a == 'TODOS':
                    total_objetivo = Residente.objects.count()
                elif aviso.dirigido_a == 'PROPIETARIOS':
                    total_objetivo = Residente.objects.filter(rol='propietario').count()
                elif aviso.dirigido_a == 'INQUILINOS':
                    total_objetivo = Residente.objects.filter(rol='inquilino').count()
                else:
                    total_objetivo = 0
                
                if total_objetivo == 0:
                    porcentaje = 0
                else:
                    porcentaje = round((total_lecturas / total_objetivo) * 100, 2)
                
                print(f"   ✅ Porcentaje: {porcentaje}% ({total_lecturas}/{total_objetivo})")
                
            except Exception as e:
                print(f"   ❌ Error en porcentaje: {e}")
        
        print(f"\n✅ Verificación completada - El admin debería funcionar ahora")
        
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    limpiar_avisos_duplicados()
    verificar_admin()