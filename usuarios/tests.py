# en usuarios/tests.py

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Residente
from condominio.models import Propiedad

class UsuariosAPITests(APITestCase):
    """
    Suite de tests FINAL para la app de usuarios, 100% sincronizada
    con los modelos y serializadores del proyecto.
    """
    def setUp(self):
        # Usuario con permisos de administrador para realizar acciones
        self.admin_user = User.objects.create_user(username='admin', password='password123', is_staff=True)
        
        # Creamos un usuario que será el propietario de la propiedad
        self.propietario_user = User.objects.create_user(
            username='propietario', 
            password='password123',
            first_name='Dueño',
            last_name='Original'
        )
        # Creamos la propiedad
        self.propiedad = Propiedad.objects.create(
            numero_casa='A-101', 
            propietario=self.propietario_user, 
            metros_cuadrados=80
        )
        # IMPORTANTE: Creamos explícitamente el perfil de Residente para el propietario
        self.residente_propietario = Residente.objects.create(
            usuario=self.propietario_user,
            propiedad=self.propiedad,
            rol='propietario'
        )
        
        self.client = APIClient()
        self.list_url = reverse('residente-list')

    def test_crear_residente_exitosamente(self):
        """
        Prueba que un admin puede crear un nuevo residente con el payload plano correcto.
        """
        self.client.force_authenticate(user=self.admin_user)
        
        # El payload debe ser plano y contener todos los campos requeridos por ResidenteWriteSerializer
        data = {
            "username": "cvaca",
            "email": "carlos.vaca@example.com",
            "password": "strongpassword123",
            "propiedad_id": self.propiedad.id,
            "rol": "inquilino"
        }
        response = self.client.post(self.list_url, data, format='json')
        
        if response.status_code != status.HTTP_201_CREATED:
            print("Error en creación:", response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Residente.objects.count(), 2) # Propietario + nuevo residente
        self.assertTrue(User.objects.filter(username='cvaca').exists())

    def test_obtener_lista_residentes(self):
        """
        Prueba que se puede obtener la lista de todos los residentes.
        """
        self.client.force_authenticate(user=self.admin_user)
        
        # La data de prueba ya se creó en setUp (el propietario)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # Solo hay un residente (el propietario)
        self.assertEqual(response.data[0]['usuario']['username'], 'propietario')

    def test_actualizar_residente_parcialmente(self):
        """
        Prueba que se pueden actualizar datos de un residente (PATCH).
        """
        self.client.force_authenticate(user=self.admin_user)
        
        # Usamos el residente que ya creamos en setUp
        residente_a_actualizar = self.residente_propietario
        
        detail_url = reverse('residente-detail', kwargs={'pk': residente_a_actualizar.pk})
        
        # El payload de actualización también es plano
        updated_data = {
            "email": "nuevo.email@dominio.com",
            "rol": "propietario" # El rol es requerido por el serializador de escritura
        }
        response = self.client.patch(detail_url, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Recargamos el objeto User desde la BD para ver los cambios
        self.propietario_user.refresh_from_db()
        self.assertEqual(self.propietario_user.email, 'nuevo.email@dominio.com')