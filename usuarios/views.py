# backend/usuarios/views.py

from django.contrib.auth.models import User

from rest_framework import viewsets, generics, permissions, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.serializers import AuthTokenSerializer

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    inline_serializer,
    OpenApiResponse,
    OpenApiExample,
)

from .models import Residente
from .serializers import (
    ResidenteReadSerializer,
    ResidenteWriteSerializer,
    RegistroSerializer,
)


# ---------------------------
# Residentes (CRUD admin)
# ---------------------------

@extend_schema_view(
    list=extend_schema(tags=["Residentes"], summary="Listar residentes"),
    retrieve=extend_schema(tags=["Residentes"], summary="Obtener residente"),
    create=extend_schema(tags=["Residentes"], summary="Crear residente"),
    update=extend_schema(tags=["Residentes"], summary="Actualizar residente"),
    partial_update=extend_schema(tags=["Residentes"], summary="Actualizar parcialmente residente"),
    destroy=extend_schema(tags=["Residentes"], summary="Eliminar residente"),
)
class ResidenteViewSet(viewsets.ModelViewSet):
    """
    CRUD de residentes (sólo admin).
    Usa serializers distintos para lectura/escritura.
    """
    queryset = Residente.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ResidenteWriteSerializer
        return ResidenteReadSerializer

    def perform_destroy(self, instance):
        """
        Al borrar el Residente, primero se borra su User asociado.
        """
        user = instance.usuario
        user.delete()


# ---------------------------
# Auth - Login (Token)
# ---------------------------

class LoginView(ObtainAuthToken):
    """
    Login con username/password. Devuelve token de DRF.
    """
    permission_classes = [AllowAny]
    serializer_class = AuthTokenSerializer

    @extend_schema(
        tags=["Auth"],
        summary="Login (Token)",
        description="Autentica con username/password y devuelve un token.",
        request=AuthTokenSerializer,
        responses={
            200: inline_serializer(
                name="LoginResponse",
                fields={"token": serializers.CharField()}
            ),
            400: OpenApiResponse(description="Credenciales inválidas"),
        },
        examples=[
            OpenApiExample(
                "Ejemplo de login",
                value={"username": "admin", "password": "admin123"}
            )
        ],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# ---------------------------
# Auth - Registro (Create)
# ---------------------------

@extend_schema(
    tags=["Auth"],
    summary="Registro de usuarios",
    description="Crea un usuario nuevo.",
    request=RegistroSerializer,
    responses={
        201: OpenApiResponse(response=RegistroSerializer, description="Usuario creado"),
        400: OpenApiResponse(description="Datos inválidos"),
        403: OpenApiResponse(description="Prohibido"),
    },
)
class RegistroView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegistroSerializer
    permission_classes = [permissions.IsAdminUser]


# ---------------------------
# Dispositivos - Registrar token FCM/APNS/Web
# ---------------------------

class RegistrarDispositivoView(APIView):
    """
    Registra/actualiza el token de notificaciones del usuario autenticado.
    """
    permission_classes = [permissions.IsAuthenticated]

    # Sólo para el esquema (silencia warnings de spectacular en APIView)
    class _SchemaSerializer(serializers.Serializer):
        device_id = serializers.CharField(required=False)
        token = serializers.CharField(help_text="Token FCM/APNS/WebPush")
        plataforma = serializers.ChoiceField(choices=["android", "ios", "web"], required=False)
        nombre = serializers.CharField(required=False)

    serializer_class = _SchemaSerializer  # usado sólo por drf-spectacular

    @extend_schema(
        tags=["Dispositivos"],
        summary="Registrar dispositivo del usuario",
        description="Guarda el token de notificaciones (FCM/APNS/WebPush) para el usuario actual.",
        request=inline_serializer(
            name="RegistrarDispositivoRequest",
            fields={
                # Acepta 'token' como principal. Si manejas 'fcm_token' por retro-compat, también.
                "token": serializers.CharField(),
                "device_id": serializers.CharField(required=False),
                "plataforma": serializers.ChoiceField(choices=["android", "ios", "web"], required=False),
                "nombre": serializers.CharField(required=False),
                # Campo alias opcional
                "fcm_token": serializers.CharField(required=False, write_only=True,
                                                    help_text="Alias opcional de 'token'"),
            }
        ),
        responses={
            200: inline_serializer(
                name="RegistrarDispositivoResponse",
                fields={
                    "ok": serializers.BooleanField(),
                    "detail": serializers.CharField(),
                }
            ),
            400: OpenApiResponse(description="Datos inválidos"),
            401: OpenApiResponse(description="No autenticado"),
        },
        examples=[
            OpenApiExample(
                "Ejemplo FCM Android",
                value={"token": "AAA.BBB.CCC", "plataforma": "android", "nombre": "Mi Pixel"}
            )
        ],
    )
    def post(self, request, *args, **kwargs):
        # Acepta 'token' y, por compatibilidad, 'fcm_token'
        token = request.data.get("token") or request.data.get("fcm_token")
        if not token:
            return Response(
                {"ok": False, "detail": "Token no fue proporcionado (use 'token' o 'fcm_token')."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            residente = Residente.objects.get(usuario=request.user)
        except Residente.DoesNotExist:
            return Response(
                {"ok": False, "detail": "El usuario no es un residente."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Guarda el token en el campo que uses en tu modelo
        # (asumo 'fcm_token'; cámbialo si tu modelo usa otro nombre)
        residente.fcm_token = token
        residente.save(update_fields=["fcm_token"])

        return Response({"ok": True, "detail": "Token registrado con éxito."}, status=status.HTTP_200_OK)
