import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import Residente
from condominio.models import Aviso, LecturaAviso

def ejemplo_uso_real():
    """Ejemplo práctico de cómo usar el sistema de seguimiento"""
    
    print("🎯 EJEMPLO PRÁCTICO: Sistema de Seguimiento de Avisos")
    print("=" * 60)
    
    # 1. Crear aviso para todos los residentes
    print("\n1️⃣  Creando aviso para TODOS los residentes...")
    aviso_general = Aviso.objects.create(
        titulo="📢 Reunión Extraordinaria - 15 de Octubre",
        contenido="""
        Estimados residentes,
        
        Se convoca a reunión extraordinaria para el día 15 de octubre a las 7:00 PM.
        
        Temas a tratar:
        - Renovación de la piscina
        - Nuevas medidas de seguridad
        - Cuotas extraordinarias
        
        Su participación es importante.
        
        Administración
        """,
        dirigido_a="TODOS",
        activo=True
    )
    print(f"   ✅ Aviso creado: {aviso_general.titulo}")
    
    # 2. Crear aviso solo para propietarios
    print("\n2️⃣  Creando aviso solo para PROPIETARIOS...")
    aviso_propietarios = Aviso.objects.create(
        titulo="🏠 Votación: Cuotas Extraordinarias",
        contenido="""
        Estimados propietarios,
        
        Se requiere su voto para aprobar las siguientes cuotas extraordinarias:
        - Renovación sistema eléctrico: $500,000
        - Pintura general edificio: $300,000
        
        Favor responder antes del 20 de octubre.
        Solo propietarios tienen derecho a voto.
        
        Administración
        """,
        dirigido_a="PROPIETARIOS",
        activo=True
    )
    print(f"   ✅ Aviso creado: {aviso_propietarios.titulo}")
    
    # 3. Simular lecturas (algunos residentes leen los avisos)
    print("\n3️⃣  Simulando que algunos residentes leen los avisos...")
    
    residentes = list(Residente.objects.all()[:5])  # Convertir a lista
    
    if len(residentes) == 0:
        print("   ❌ No hay residentes en la base de datos")
        return
    
    # Simular que 3 residentes leen el aviso general
    for i, residente in enumerate(residentes[:3]):
        lectura, created = LecturaAviso.objects.get_or_create(
            aviso=aviso_general,
            residente=residente
        )
        if created:
            print(f"   📖 {residente.usuario.username} leyó el aviso general")
    
    # Simular que solo los propietarios leen el aviso de propietarios
    propietarios = [r for r in residentes if r.rol == 'propietario']  # Filtrar en Python
    for propietario in propietarios[:2]:  # Solo 2 propietarios lo leen
        lectura, created = LecturaAviso.objects.get_or_create(
            aviso=aviso_propietarios,
            residente=propietario
        )
        if created:
            print(f"   📖 {propietario.usuario.username} leyó el aviso de propietarios")
    
    # 4. Mostrar estadísticas detalladas
    print("\n4️⃣  ESTADÍSTICAS DE SEGUIMIENTO:")
    print("=" * 40)
    
    for aviso in [aviso_general, aviso_propietarios]:
        print(f"\n🔹 {aviso.titulo}")
        print(f"   📊 Dirigido a: {aviso.get_dirigido_a_display()}")
        print(f"   🎯 Residentes objetivo: {aviso.total_residentes_objetivo()}")
        print(f"   ✅ Total lecturas: {aviso.total_lecturas()}")
        print(f"   📈 Porcentaje leído: {aviso.porcentaje_lectura()}%")
        
        # Mostrar quién leyó
        lecturas = aviso.lecturas.select_related('residente__usuario')
        if lecturas.exists():
            print(f"   📖 Residentes que leyeron:")
            for lectura in lecturas:
                print(f"      - {lectura.residente.usuario.username} ({lectura.residente.rol}) - {lectura.fecha_lectura.strftime('%d/%m/%Y %H:%M')}")
        
        # Mostrar quién NO leyó (solo los primeros 5 para no llenar la pantalla)
        residentes_objetivo = Residente.objects.all()
        if aviso.dirigido_a == 'PROPIETARIOS':
            residentes_objetivo = residentes_objetivo.filter(rol='propietario')
        elif aviso.dirigido_a == 'INQUILINOS':
            residentes_objetivo = residentes_objetivo.filter(rol='inquilino')
        
        residentes_que_leyeron = lecturas.values_list('residente_id', flat=True) if lecturas.exists() else []
        residentes_sin_leer = residentes_objetivo.exclude(id__in=residentes_que_leyeron)[:5]
        
        if residentes_sin_leer.exists():
            print(f"   ❌ Residentes que NO han leído (mostrando primeros 5):")
            for residente in residentes_sin_leer:
                print(f"      - {residente.usuario.username} ({residente.rol})")
        else:
            print(f"   🎉 ¡Todos los residentes objetivo han leído este aviso!")
    
    # 5. Ejemplo de consultas útiles para administradores
    print("\n5️⃣  CONSULTAS ÚTILES PARA ADMINISTRADORES:")
    print("=" * 45)
    
    # Avisos con bajo porcentaje de lectura
    avisos_bajo_porcentaje = []
    for aviso in Aviso.objects.filter(activo=True):
        if aviso.porcentaje_lectura() < 50:
            avisos_bajo_porcentaje.append(aviso)
    
    if avisos_bajo_porcentaje:
        print("\n⚠️  Avisos con BAJO porcentaje de lectura (< 50%):")
        for aviso in avisos_bajo_porcentaje:
            print(f"   - {aviso.titulo}: {aviso.porcentaje_lectura()}%")
            print(f"     💡 Sugerencia: Enviar recordatorio o notificación push")
    
    # Residentes que no han leído ningún aviso reciente
    print("\n🔍 Análisis de participación:")
    from django.utils import timezone
    from datetime import timedelta
    
    # Avisos de los últimos 30 días
    fecha_limite = timezone.now() - timedelta(days=30)
    avisos_recientes = Aviso.objects.filter(fecha_publicacion__gte=fecha_limite, activo=True)
    
    if avisos_recientes.exists():
        print(f"   📅 Avisos activos de los últimos 30 días: {avisos_recientes.count()}")
        
        # Encontrar residentes menos participativos
        residentes_poco_participativos = []
        for residente in Residente.objects.all()[:10]:  # Revisar primeros 10
            lecturas_recientes = LecturaAviso.objects.filter(
                residente=residente,
                aviso__in=avisos_recientes
            ).count()
            
            porcentaje_participacion = (lecturas_recientes / avisos_recientes.count()) * 100 if avisos_recientes.count() > 0 else 0
            
            if porcentaje_participacion < 30:  # Menos del 30% de participación
                residentes_poco_participativos.append((residente, porcentaje_participacion))
        
        if residentes_poco_participativos:
            print(f"   ⚠️  Residentes con baja participación (< 30%):")
            for residente, porcentaje in residentes_poco_participativos[:5]:
                print(f"      - {residente.usuario.username}: {porcentaje:.1f}% de avisos leídos")
    
    # 6. Limpiar datos de ejemplo
    print(f"\n6️⃣  Limpiando datos de ejemplo...")
    aviso_general.delete()
    aviso_propietarios.delete()
    print("   🧹 Avisos de ejemplo eliminados")
    
    print(f"\n🎉 DEMOSTRACIÓN COMPLETADA")
    print("=" * 30)
    print("✅ Sistema funcionando correctamente")
    print("✅ Puedes rastrear qué residentes leen cada aviso")
    print("✅ Estadísticas detalladas disponibles")
    print("✅ Información útil para tomar decisiones")

if __name__ == "__main__":
    ejemplo_uso_real()