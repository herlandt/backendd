# en mantenimiento/tests.py

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from .models import SolicitudMantenimiento, PersonalMantenimiento
from condominio.models import Propiedad
from usuarios.models import Residente

class MantenimientoAPITests(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_user(username='admin', password='password123', is_staff=True)
        self.residente_user = User.objects.create_user(username='residente', password='password123')
        
        self.propiedad = Propiedad.objects.create(numero_casa='D-401', propietario=self.residente_user, metros_cuadrados=95)
        self.residente = Residente.objects.create(usuario=self.residente_user, propiedad=self.propiedad, rol='propietario')
        
        self.client = APIClient()
        self.solicitud_list_url = reverse('solicitud-mantenimiento-list')

    def test_residente_crea_solicitud_mantenimiento(self):
        """Prueba que un residente puede crear una solicitud de mantenimiento."""
        self.client.force_authenticate(user=self.residente_user)
        
        # El serializador espera 'propiedad_id', 'titulo', y 'descripcion'.
        # 'solicitado_por' lo añade la vista automáticamente.
        data = {
            'propiedad_id': self.propiedad.id,
            'titulo': 'La luz del poste de la piscina está parpadeando.',
            'descripcion': 'Necesita revisión.'
        }
        response = self.client.post(self.solicitud_list_url, data, format='json')
            
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SolicitudMantenimiento.objects.count(), 1)
        self.assertEqual(SolicitudMantenimiento.objects.get().solicitado_por, self.residente_user)

    def test_admin_asigna_y_completa_solicitud(self):
        """Prueba el flujo completo de una solicitud: asignación y finalización."""
        self.client.force_authenticate(user=self.admin_user)
        
        solicitud = SolicitudMantenimiento.objects.create(
            propiedad=self.propiedad,
            titulo='Fuga de agua en jardinera',
            solicitado_por=self.residente_user
        )
        # Corregido: El modelo no tiene 'apellido'.
        personal = PersonalMantenimiento.objects.create(nombre='Juan Rios', especialidad='plomeria')
        
        detail_url = reverse('solicitud-mantenimiento-detail', kwargs={'pk': solicitud.pk})
        
        update_data = {'asignado_a_id': personal.id, 'estado': 'EN_PROGRESO'}
        response = self.client.patch(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        complete_data = {'estado': 'FINALIZADA'}
        response = self.client.patch(detail_url, complete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, 'FINALIZADA')