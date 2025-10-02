# Script de prueba para sistema de auditoría y notificaciones
# Para ejecutar: python manage.py shell < test_auditoria_notificaciones.py

from django.contrib.auth.models import User
from django.utils import timezone
from condominio.models import Propiedad
from finanzas.models import Gasto, Multa
from seguridad.models import Visitante
from auditoria.models import Bitacora
from auditoria.eventos import (
    notificar_gasto_asignado, 
    notificar_multa_asignada, 
    notificar_visitante_registrado
)

print("=== PROBANDO SISTEMA DE AUDITORÍA Y NOTIFICACIONES ===")

# 1. Crear usuarios de prueba si no existen
admin_user, created = User.objects.get_or_create(
    username='admin_test',
    defaults={
        'email': 'admin@test.com',
        'first_name': 'Admin',
        'last_name': 'Test',
        'is_staff': True
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()
    print(f"✅ Usuario admin creado: {admin_user.username}")
else:
    print(f"✅ Usuario admin existente: {admin_user.username}")

residente_user, created = User.objects.get_or_create(
    username='residente_test',
    defaults={
        'email': 'residente@test.com',
        'first_name': 'Residente',
        'last_name': 'Test'
    }
)
if created:
    residente_user.set_password('residente123')
    residente_user.save()
    print(f"✅ Usuario residente creado: {residente_user.username}")
else:
    print(f"✅ Usuario residente existente: {residente_user.username}")

# 2. Crear propiedad de prueba si no existe
propiedad, created = Propiedad.objects.get_or_create(
    numero_casa='001',
    defaults={
        'propietario': admin_user,
        'metros_cuadrados': 120.50
    }
)
if created:
    print(f"✅ Propiedad creada: Casa {propiedad.numero_casa}")
else:
    print(f"✅ Propiedad existente: Casa {propiedad.numero_casa}")

# 3. Probar notificación de gasto
print("\n--- PROBANDO NOTIFICACIÓN DE GASTO ---")
try:
    notificar_gasto_asignado(
        usuario_accion=admin_user,
        ip_address='192.168.1.100',
        propiedad_id=propiedad.id,
        monto='150.00',
        descripcion='Expensa mensual de prueba'
    )
    print("✅ Notificación de gasto enviada correctamente")
except Exception as e:
    print(f"❌ Error al notificar gasto: {e}")

# 4. Probar notificación de multa
print("\n--- PROBANDO NOTIFICACIÓN DE MULTA ---")
try:
    notificar_multa_asignada(
        usuario_accion=admin_user,
        ip_address='192.168.1.100',
        propiedad_id=propiedad.id,
        monto='50.00',
        concepto='Ruido excesivo'
    )
    print("✅ Notificación de multa enviada correctamente")
except Exception as e:
    print(f"❌ Error al notificar multa: {e}")

# 5. Probar notificación de visitante
print("\n--- PROBANDO NOTIFICACIÓN DE VISITANTE ---")
try:
    notificar_visitante_registrado(
        usuario_accion=admin_user,
        ip_address='192.168.1.100',
        propiedad_id=propiedad.id,
        nombre_visitante='Juan Pérez'
    )
    print("✅ Notificación de visitante enviada correctamente")
except Exception as e:
    print(f"❌ Error al notificar visitante: {e}")

# 6. Verificar registros de auditoría
print("\n--- VERIFICANDO REGISTROS DE AUDITORÍA ---")
registros_recientes = Bitacora.objects.filter(
    timestamp__gte=timezone.now() - timezone.timedelta(minutes=5)
).order_by('-timestamp')

if registros_recientes.exists():
    print(f"✅ Se encontraron {registros_recientes.count()} registros de auditoría recientes:")
    for registro in registros_recientes[:5]:  # Mostrar solo los 5 más recientes
        print(f"  - {registro.timestamp.strftime('%H:%M:%S')} | {registro.accion} | {registro.usuario}")
else:
    print("❌ No se encontraron registros de auditoría recientes")

print("\n=== PRUEBA COMPLETADA ===")