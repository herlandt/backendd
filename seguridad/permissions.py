# en seguridad/tests_permisos.py

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from condominio.models import Propiedad
# seguridad/permissions.py
from django.conf import settings
from rest_framework.permissions import BasePermission


class HasAPIKey(BasePermission):
    """
    Permite el acceso cuando el header X-API-KEY coincide con settings.SECURITY_API_KEY.
    Úsalo sólo en endpoints que realmente lo necesiten.
    """
    message = "Falta X-API-KEY o es inválida."

    def has_permission(self, request, view):
        expected = getattr(settings, "SECURITY_API_KEY", None)
        # admite tanto request.headers como META por compatibilidad
        provided = request.headers.get("X-API-KEY") or request.META.get("HTTP_X_API_KEY")
        return bool(expected) and provided == expected


# (Opcional) Si necesitas roles, puedes mantener algo así:
# from usuarios.models import Usuario
#
# class EsResidente(BasePermission):
#     def has_permission(self, request, view):
#         return bool(request.user and request.user.is_authenticated
#                     and getattr(request.user, "rol", None) == Usuario.Roles.RESIDENTE)
#
# class EsGuardia(BasePermission):
#     def has_permission(self, request, view):
#         return bool(request.user and request.user.is_authenticated
#                     and getattr(request.user, "rol", None) == Usuario.Roles.GUARDIA)
#
# class EsAdministrador(BasePermission):
#     def has_permission(self, request, view):
#         return bool(request.user and request.user.is_authenticated
#                     and (request.user.is_staff or
#                          getattr(request.user, "rol", None) == Usuario.Roles.ADMIN))

class PermissionsTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'password123')
        cls.staff_user = User.objects.create_user('staff', 'staff@example.com', 'password123', is_staff=True)
        cls.normal_user = User.objects.create_user('user', 'user@example.com', 'password123')
        cls.p = Propiedad.objects.create(numero_casa="TEST-1", propietario=cls.normal_user, metros_cuadrados=80)
        cls.url_control_acceso = reverse('control-acceso-vehicular')

    def test_staff_can_access_endpoint(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(self.url_control_acceso, {"placa": "NOEXISTE"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_normal_user_cannot_access_endpoint(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post(self.url_control_acceso, {"placa": "NOEXISTE"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)