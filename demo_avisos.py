import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import Residente
from condominio.models import Aviso, LecturaAviso

def demo_seguimiento_avisos():
    print("DEMO: Sistema de Seguimiento de Lectura de Avisos")
    print("=" * 50)
    
    # 1. Crear un aviso de ejemplo
    aviso = Aviso.objects.create(
        titulo="Reunion de Condominios - Octubre 2025",
        contenido="Se convoca a todos los residentes a la reunion general.",
        dirigido_a="TODOS"
    )
    print(f"✅ Aviso creado: {aviso.titulo}")
    
    # 2. Obtener algunos residentes existentes
    residentes = Residente.objects.all()[:3]  # Tomar los primeros 3
    print(f"📋 Residentes encontrados: {residentes.count()}")
    
    for residente in residentes:
        print(f"   - {residente.usuario.username} ({residente.rol})")
    
    if residentes.count() == 0:
        print("❌ No hay residentes. Necesitas crear residentes primero.")
        return
    
    # 3. Simular que algunos residentes leyeron el aviso
    print("\n📖 Simulando lecturas...")
    for i, residente in enumerate(residentes):
        if i < 2:  # Solo los primeros 2 leen el aviso
            lectura, created = LecturaAviso.objects.get_or_create(
                aviso=aviso,
                residente=residente
            )
            if created:
                print(f"   ✅ {residente.usuario.username} leyó el aviso")
    
    # 4. Mostrar estadísticas
    print(f"\n📊 ESTADÍSTICAS DEL AVISO:")
    print(f"   Título: {aviso.titulo}")
    print(f"   Dirigido a: {aviso.dirigido_a}")
    print(f"   Total residentes objetivo: {aviso.total_residentes_objetivo()}")
    print(f"   Total que leyeron: {aviso.total_lecturas()}")
    print(f"   Porcentaje de lectura: {aviso.porcentaje_lectura()}%")
    
    print(f"\n📖 RESIDENTES QUE LEYERON:")
    for lectura in aviso.lecturas.all():
        print(f"   - {lectura.residente.usuario.username} el {lectura.fecha_lectura}")
    
    print(f"\n❌ RESIDENTES QUE NO HAN LEÍDO:")
    # Obtener residentes que no han leído
    residentes_que_leyeron = aviso.lecturas.values_list('residente_id', flat=True)
    residentes_sin_leer = Residente.objects.exclude(id__in=residentes_que_leyeron)
    
    for residente in residentes_sin_leer:
        print(f"   - {residente.usuario.username} ({residente.rol})")
    
    # 5. Limpiar
    print(f"\n🧹 Limpiando datos de prueba...")
    aviso.delete()
    print("   ✅ Aviso eliminado")

if __name__ == "__main__":
    demo_seguimiento_avisos()