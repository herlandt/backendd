# views.py - Vista de Bienvenida para la API
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework import serializers
from drf_spectacular.utils import extend_schema

class APIWelcomeResponseSerializer(serializers.Serializer):
    """Serializer para la respuesta de la vista de bienvenida"""
    mensaje = serializers.CharField()
    version = serializers.CharField()
    fecha = serializers.CharField()
    estado = serializers.CharField()

@extend_schema(
    description="Vista de bienvenida de la API del Sistema de Gestión de Condominios",
    summary="API Welcome",
    responses={200: APIWelcomeResponseSerializer}
)
class APIWelcomeView(APIView):
    """
    Vista de bienvenida que proporciona información básica sobre la API
    """
    permission_classes = [AllowAny]
    serializer_class = APIWelcomeResponseSerializer
    
    def get(self, request):
        return Response({
            "mensaje": "¡Bienvenido a la API del Sistema de Gestión de Condominios!",
            "version": "1.0.0",
            "fecha": "2025-09-30",
            "estado": "Operativo",
            "documentacion": {
                "swagger_ui": "/api/schema/swagger-ui/",
                "redoc": "/api/schema/redoc/",
                "openapi_schema": "/api/schema/"
            },
            "endpoints_principales": {
                "autenticacion": "/api/login/",
                "registro": "/api/registro/",
                "usuarios": "/api/usuarios/",
                "seguridad": "/api/seguridad/",
                "condominio": "/api/condominio/",
                "finanzas": "/api/finanzas/",
                "mantenimiento": "/api/mantenimiento/",
                "notificaciones": "/api/notificaciones/"
            },
            "informacion_tecnica": {
                "framework": "Django 5.2.6",
                "rest_framework": "Django REST Framework",
                "autenticacion": "Token Authentication",
                "documentacion": "drf-spectacular (OpenAPI 3.0)"
            }
        }, status=status.HTTP_200_OK)