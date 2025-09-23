# usuarios/management/commands/populate_db.py

import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import date, time, timedelta

# Importamos los modelos desde sus nuevas apps correctas
from usuarios.models import Residente
from condominio.models import Propiedad, AreaComun
from finanzas.models import Gasto, Reserva
from seguridad.models import Vehiculo
from mantenimiento.models import PersonalMantenimiento, SolicitudMantenimiento

class Command(BaseCommand):
    help = 'Puebla la base de datos con datos de prueba para el Smart Condominium'

    def handle(self, *args, **kwargs):
        self.stdout.write("Limpiando la base de datos antigua...")
        # Limpiamos los datos para evitar duplicados, excepto los superusuarios
        User.objects.filter(is_superuser=False).delete()
        Propiedad.objects.all().delete()
        AreaComun.objects.all().delete()
        # El resto se borra en cascada (residentes, gastos, etc.)
        
        self.stdout.write("Creando nuevos datos de prueba...")

        # --- 1. Crear Usuarios ---
        user_ana = User.objects.create_user('ana_gomez', 'ana@email.com', 'password123')
        user_ana.first_name = 'Ana'
        user_ana.last_name = 'Gomez'
        user_ana.save()

        user_luis = User.objects.create_user('luis_perez', 'luis@email.com', 'password123')
        user_luis.first_name = 'Luis'
        user_luis.last_name = 'Perez'
        user_luis.save()

        user_juan = User.objects.create_user('juan_tecnico', 'juan@email.com', 'password123')
        user_juan.first_name = 'Juan'
        user_juan.last_name = 'Rodriguez'
        user_juan.save()
        
        self.stdout.write("-> Usuarios creados")

        # --- 2. Crear Propiedades ---
        propiedad_a101 = Propiedad.objects.create(numero_casa='A101', propietario=user_ana, metros_cuadrados=120)
        propiedad_b205 = Propiedad.objects.create(numero_casa='B205', propietario=user_luis, metros_cuadrados=95)
        
        self.stdout.write("-> Propiedades creadas")

        # --- 3. Crear Residentes (vincular usuarios a propiedades) ---
        Residente.objects.create(usuario=user_ana, propiedad=propiedad_a101, rol='propietario')
        Residente.objects.create(usuario=user_luis, propiedad=propiedad_b205, rol='inquilino')

        self.stdout.write("-> Residentes creados y vinculados")

        # --- 4. Crear Personal de Mantenimiento ---
        PersonalMantenimiento.objects.create(usuario=user_juan, especialidad='Electricista', activo=True)
        
        self.stdout.write("-> Personal de Mantenimiento creado")

        # --- 5. Crear Vehículos ---
        Vehiculo.objects.create(propiedad=propiedad_a101, placa='TULIO31', marca='Mercedes', modelo='Clase E')
        Vehiculo.objects.create(propiedad=propiedad_b205, placa='XYZ789', marca='Nissan', modelo='Versa')
        
        self.stdout.write("-> Vehículos creados")

        # --- 6. Crear Áreas Comunes ---
        piscina = AreaComun.objects.create(
            nombre='Piscina', descripcion='Área de piscina y recreación', capacidad=30,
            costo_reserva=50.00, horario_apertura=time(9,0), horario_cierre=time(21,0)
        )
        salon = AreaComun.objects.create(
            nombre='Salón de Eventos', descripcion='Salón para fiestas y reuniones', capacidad=50,
            costo_reserva=250.00
        )
        
        self.stdout.write("-> Áreas Comunes creadas")

        # --- 7. Crear Gastos Mensuales ---
        Gasto.objects.create(
            propiedad=propiedad_a101, monto=150.00, 
            fecha_vencimiento=date.today() + timedelta(days=15),
            descripcion='Expensas del mes'
        )
        gasto_pagado = Gasto.objects.create(
            propiedad=propiedad_b205, monto=125.00,
            fecha_vencimiento=date.today() - timedelta(days=30), # Vencido
            descripcion='Cuota extraordinaria',
            pagado=True
        )
        
        self.stdout.write("-> Gastos creados")

        # --- 8. Crear Solicitudes de Mantenimiento ---
        SolicitudMantenimiento.objects.create(
            solicitado_por=user_ana, propiedad=propiedad_a101,
            titulo='Luz del pasillo quemada',
            descripcion='La luz del pasillo del Bloque A, piso 1 no enciende.'
        )

        self.stdout.write("-> Solicitudes de Mantenimiento creadas")

        self.stdout.write(self.style.SUCCESS('¡Base de datos poblada con éxito!'))
        self.stdout.write("Usuarios de prueba:")
        self.stdout.write("  - Residente: ana_gomez / password123")
        self.stdout.write("  - Residente: luis_perez / password123")
        self.stdout.write("  - Mantenimiento: juan_tecnico / password123")