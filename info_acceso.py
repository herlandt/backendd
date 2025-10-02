import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from condominio.models import Aviso, LecturaAviso
from usuarios.models import Residente

def mostrar_desde_donde():
    """Muestra información sobre desde dónde se están haciendo las consultas"""
    
    print("🌍 INFORMACIÓN DE ACCESO AL SISTEMA")
    print("=" * 50)
    
    # 1. Mostrar avisos recientes con lecturas
    print("\n📋 AVISOS RECIENTES CON SEGUIMIENTO:")
    avisos = Aviso.objects.filter(activo=True).order_by('-fecha_publicacion')[:5]
    
    if not avisos.exists():
        print("   ❌ No hay avisos activos")
        return
    
    for aviso in avisos:
        print(f"\n🔹 {aviso.titulo}")
        print(f"   📅 Publicado: {aviso.fecha_publicacion.strftime('%d/%m/%Y %H:%M')}")
        print(f"   🎯 Dirigido a: {aviso.get_dirigido_a_display()}")
        print(f"   📊 Lecturas: {aviso.total_lecturas()} de {aviso.total_residentes_objetivo()} ({aviso.porcentaje_lectura()}%)")
        
        # Mostrar lecturas recientes con IP
        lecturas_recientes = aviso.lecturas.order_by('-fecha_lectura')[:3]
        if lecturas_recientes.exists():
            print(f"   📖 Últimas lecturas:")
            for lectura in lecturas_recientes:
                ip_info = f" desde {lectura.ip_lectura}" if lectura.ip_lectura else ""
                print(f"      - {lectura.residente.usuario.username} ({lectura.fecha_lectura.strftime('%d/%m/%Y %H:%M')}){ip_info}")
    
    # 2. Estadísticas generales de acceso
    print(f"\n📈 ESTADÍSTICAS GENERALES:")
    total_lecturas = LecturaAviso.objects.count()
    total_residentes = Residente.objects.count()
    
    print(f"   👥 Total residentes: {total_residentes}")
    print(f"   📖 Total lecturas registradas: {total_lecturas}")
    
    if total_lecturas > 0:
        # IPs más frecuentes
        from django.db.models import Count
        ips_frecuentes = LecturaAviso.objects.filter(
            ip_lectura__isnull=False
        ).values('ip_lectura').annotate(
            total=Count('id')
        ).order_by('-total')[:5]
        
        if ips_frecuentes.exists():
            print(f"\n🌐 IPs MÁS FRECUENTES:")
            for ip_data in ips_frecuentes:
                print(f"   - {ip_data['ip_lectura']}: {ip_data['total']} lecturas")
        
        # Residentes más activos
        residentes_activos = LecturaAviso.objects.values(
            'residente__usuario__username'
        ).annotate(
            total=Count('id')
        ).order_by('-total')[:5]
        
        if residentes_activos.exists():
            print(f"\n👑 RESIDENTES MÁS ACTIVOS:")
            for residente_data in residentes_activos:
                print(f"   - {residente_data['residente__usuario__username']}: {residente_data['total']} avisos leídos")
    
    # 3. Información del servidor
    print(f"\n🖥️  INFORMACIÓN DEL SERVIDOR:")
    print(f"   🌐 Backend ejecutándose en: http://0.0.0.0:8000")
    print(f"   📱 API disponible en: http://0.0.0.0:8000/api/")
    print(f"   🛡️  Panel admin en: http://0.0.0.0:8000/admin/")
    
    print(f"\n🔗 ENDPOINTS DE AVISOS:")
    print(f"   📋 Listar avisos: GET /api/condominio/avisos/")
    print(f"   📖 Marcar como leído: POST /api/condominio/avisos/{{id}}/marcar_como_leido/")
    print(f"   📊 Estadísticas: GET /api/condominio/avisos/{{id}}/estadisticas_lectura/")
    print(f"   📱 Mis pendientes: GET /api/condominio/avisos/mis_avisos_pendientes/")

def mostrar_ultimas_actividades():
    """Muestra las últimas actividades del sistema"""
    
    print(f"\n🕒 ÚLTIMAS ACTIVIDADES (últimas 10):")
    print("-" * 40)
    
    lecturas_recientes = LecturaAviso.objects.select_related(
        'residente__usuario', 'aviso'
    ).order_by('-fecha_lectura')[:10]
    
    if lecturas_recientes.exists():
        for lectura in lecturas_recientes:
            fecha_str = lectura.fecha_lectura.strftime('%d/%m/%Y %H:%M')
            ip_str = f" desde {lectura.ip_lectura}" if lectura.ip_lectura else ""
            print(f"   📖 {fecha_str} - {lectura.residente.usuario.username} leyó '{lectura.aviso.titulo[:30]}...'{ip_str}")
    else:
        print("   ℹ️  No hay actividad reciente registrada")

if __name__ == "__main__":
    mostrar_desde_donde()
    mostrar_ultimas_actividades()