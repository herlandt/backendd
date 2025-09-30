# En usuarios/permissions.py
from rest_framework.permissions import BasePermission
from .models import UserProfile

class IsPropietario(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            return request.user.profile.role == UserProfile.Role.PROPIETARIO
        except UserProfile.DoesNotExist:
            return False

class IsPersonalSeguridad(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            return request.user.profile.role == UserProfile.Role.SEGURIDAD
        except UserProfile.DoesNotExist:
            return False

class IsPersonalMantenimiento(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            return request.user.profile.role == UserProfile.Role.MANTENIMIENTO
        except UserProfile.DoesNotExist:
            return False

class IsResidente(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            return request.user.profile.role == UserProfile.Role.RESIDENTE
        except UserProfile.DoesNotExist:
            return False

class IsPropietarioOrReadOnly(BasePermission):
    """
    Permite crear/editar/eliminar solo a propietarios, pero cualquier usuario autenticado puede leer.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        try:
            return request.user.profile.role == UserProfile.Role.PROPIETARIO
        except UserProfile.DoesNotExist:
            return False