# en usuarios/management/commands/seed_all.py

import random
from datetime import datetime, timedelta, date
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from faker import Faker

# Importar modelos de todas las aplicaciones
from usuarios.models import Residente
from condominio.models import Propiedad, AreaComun
from finanzas.models import Gasto, Multa, Pago, Reserva
from mantenimiento.models import SolicitudMantenimiento, PersonalMantenimiento
from seguridad.models import Visitante, Visita, Vehiculo

class Command(BaseCommand):
    help = 'Puebla la base de datos con datos de prueba completos para todas las aplicaciones.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando el poblado de la base de datos...'))
        
        with transaction.atomic():
            self.limpiar_base_de_datos()
            self.crear_datos()

        self.stdout.write(self.style.SUCCESS('¡Base de datos poblada exitosamente! ¡Misión cumplida!'))

    def limpiar_base_de_datos(self):
        self.stdout.write('Limpiando la base de datos...')
        
        Visita.objects.all().delete()
        Visitante.objects.all().delete()
        Vehiculo.objects.all().delete()
        Pago.objects.all().delete()
        Gasto.objects.all().delete()
        Multa.objects.all().delete()
        Reserva.objects.all().delete()
        SolicitudMantenimiento.objects.all().delete()
        PersonalMantenimiento.objects.all().delete()
        Residente.objects.all().delete()
        Propiedad.objects.all().delete()
        AreaComun.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        
        self.stdout.write(self.style.WARNING('Datos antiguos eliminados.'))

    def crear_datos(self):
        fake = Faker('es_ES')

        self.stdout.write('Creando usuario administrador...')
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@condominio.com', 'first_name': 'Admin', 'last_name': 'Condominio', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Usuario admin creado con contraseña "admin123"'))

        self.stdout.write('Creando áreas comunes...')
        areas_comunes_nombres = ['Piscina', 'Salón de Eventos', 'Churrasquera', 'Cancha de Tenis']
        areas_comunes = [AreaComun.objects.create(nombre=nombre, capacidad=random.randint(10, 50)) for nombre in areas_comunes_nombres]

        self.stdout.write('Creando personal de mantenimiento...')
        especialidades = ['Electricista', 'Plomero', 'Jardinero', 'General']
        personal_mantenimiento = [PersonalMantenimiento.objects.create(
            nombre=f"{fake.first_name()} {fake.last_name()}",
            telefono=fake.phone_number(),
            especialidad=random.choice(especialidades)
        ) for _ in range(4)]

        self.stdout.write('Creando propietarios, residentes y propiedades...')
        residentes_creados = []
        for i in range(10):
            propietario_user = User.objects.create_user(username=f'propietario{i+1}', password='password123', first_name=fake.first_name(), last_name=fake.last_name(), email=fake.email())
            propiedad = Propiedad.objects.create(numero_casa=f'C-{100+i}', propietario=propietario_user, metros_cuadrados=random.uniform(80.0, 250.0))
            residente = Residente.objects.create(usuario=propietario_user, propiedad=propiedad)
            residentes_creados.append(residente)
            
            if i % 2 == 0:
                inquilino_user = User.objects.create_user(username=f'inquilino{i+1}', password='password123', first_name=fake.first_name(), last_name=fake.last_name(), email=fake.email())
                residente_inquilino = Residente.objects.create(usuario=inquilino_user, propiedad=propiedad)
                residentes_creados.append(residente_inquilino)
        
        self.stdout.write('Creando gastos, multas y pagos...')
        propiedades = Propiedad.objects.all()
        for prop in propiedades:
            for j in range(3):
                fecha_emision = date.today() - timedelta(days=30*j)
                gasto = Gasto.objects.create(
                    propiedad=prop,
                    monto=random.uniform(300.0, 800.0),
                    fecha_emision=fecha_emision,
                    fecha_vencimiento=fecha_emision + timedelta(days=15),
                    descripcion=f'Expensas {fecha_emision.strftime("%B %Y")}',
                    pagado=(j > 0)
                )
                if gasto.pagado:
                    fecha_de_pago = fecha_emision + timedelta(days=random.randint(1,10))
                    Pago.objects.create(
                        gasto=gasto,
                        usuario=prop.propietario,
                        monto_pagado=gasto.monto,
                        fecha_pago=fecha_de_pago,
                        estado_pago='completado'
                    )
            
            if prop.id % 3 == 0:
                Multa.objects.create(
                    propiedad=prop,
                    monto=random.uniform(50.0, 200.0),
                    concepto='Ruido excesivo en horario no permitido',
                    fecha_emision=date.today() - timedelta(days=random.randint(5, 20)),
                    pagado=False
                )

        self.stdout.write('Creando visitas y visitantes...')
        for _ in range(15):
            residente_anfitrion = random.choice(residentes_creados)
            visitante = Visitante.objects.create(
                nombre_completo=f"{fake.first_name()} {fake.last_name()}",
                documento=fake.ssn()
            )
            
            # --- CORRECCIÓN FINAL (AHORA SÍ) ---
            fecha_programada = datetime.now() + timedelta(days=random.randint(-2, 2))
            Visita.objects.create(
                visitante=visitante,
                propiedad=residente_anfitrion.propiedad, # La visita es a la propiedad
                fecha_ingreso_programado=fecha_programada,
                fecha_salida_programada=fecha_programada + timedelta(hours=3),
                ingreso_real=fecha_programada - timedelta(minutes=random.randint(5, 30)) # El visitante llegó un poco antes
            )
            # --- FIN CORRECCIÓN ---

        self.stdout.write('Creando solicitudes de mantenimiento...')
        for _ in range(5):
            solicitante = random.choice(residentes_creados)
            solicitud = SolicitudMantenimiento.objects.create(
                propiedad=solicitante.propiedad,
                solicitado_por=solicitante.usuario,
                titulo=f'Problema con {random.choice(["tubería", "luz", "puerta"])}',
                descripcion=f'Revisar {random.choice(["fuga", "cortocircuito", "cerradura"])} en el área de la cocina.',
                estado=random.choice(['PENDIENTE', 'EN_PROGRESO', 'FINALIZADA'])
            )
            if solicitud.estado != 'PENDIENTE':
                solicitud.asignado_a = random.choice(personal_mantenimiento)
                solicitud.save()