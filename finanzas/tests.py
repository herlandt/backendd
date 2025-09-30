# en finanzas/tests.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Gasto, Pago
from condominio.models import Propiedad
from usuarios.models import UserProfile
from datetime import date

class FinanzasAPITests(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_user(username='admin', password='password123', is_staff=True)
        self.propietario_user = User.objects.create_user(username='propietario', password='password123')
        
        # Actualizar directamente los UserProfiles creados por las señales
        self.admin_user.profile.role = UserProfile.Role.PROPIETARIO
        self.admin_user.profile.save()
        
        self.propietario_user.profile.role = UserProfile.Role.RESIDENTE
        self.propietario_user.profile.save()
        
        self.propiedad = Propiedad.objects.create(
            numero_casa='B-201', 
            propietario=self.propietario_user, 
            metros_cuadrados=120.50
        )
        
        self.client.force_authenticate(user=self.admin_user)
        self.gasto_list_url = reverse('gasto-list')
        self.pago_list_url = reverse('pago-list')

    def test_crear_gasto_comun(self):
        """Asegura que un admin pueda crear un nuevo gasto común."""
        data = {
            'propiedad': self.propiedad.id,
            'monto': '250.50',
            'fecha_emision': '2025-10-01',
            'fecha_vencimiento': '2025-10-31',
            'descripcion': 'Expensas Octubre 2025',
            'mes': 10,
            'anio': 2025
        }
        response = self.client.post(self.gasto_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Gasto.objects.count(), 1)
    
    def test_registrar_pago_total_y_verificar_gasto(self):
        """Asegura que un pago total marque el gasto como pagado."""
        gasto = Gasto.objects.create(
            propiedad=self.propiedad,
            monto='300.00',
            fecha_emision=date(2025, 11, 1),
            fecha_vencimiento='2025-11-10',
            descripcion='Cuota Extra Mantenimiento',
            mes=11, anio=2025
        )
        
        data = {'gasto': gasto.id, 'monto_pagado': '300.00'}
        response = self.client.post(self.pago_list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        gasto.refresh_from_db()
        self.assertTrue(gasto.pagado)

    def test_pago_parcial_no_cambia_estado_gasto(self):
        """Asegura que un pago parcial NO marque el gasto como pagado."""
        gasto = Gasto.objects.create(
            propiedad=self.propiedad,
            monto='500.00',
            fecha_emision=date(2025, 12, 1),
            fecha_vencimiento='2025-12-31',
            descripcion='Expensas Diciembre',
            mes=12, anio=2025
        )
        
        data = {'gasto': gasto.id, 'monto_pagado': '200.00'}
        self.client.post(self.pago_list_url, data, format='json')
        
        gasto.refresh_from_db()
        self.assertFalse(gasto.pagado)