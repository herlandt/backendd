# backend/usuarios/views.py

from django.contrib.auth.models import User

from rest_framework import viewsets, generics, permissions, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.serializers import AuthTokenSerializer
import boto3
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
# seguridad/views.py

# ... (importaciones existentes) ...
# <-- Para buscar a los administradores

# ... (el resto de tus importaciones) ...
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    inline_serializer,
    OpenApiResponse,
    OpenApiExample,
)
# usuarios/views.py

# ... (importaciones existentes) ...
import boto3
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
# ...
from .models import Residente
from .serializers import (
    ResidenteReadSerializer,
    ResidenteWriteSerializer,
    RegistroSerializer,
)

from notificaciones.services import notificar_usuario # <-- Servicio para enviar notificaciones
from usuarios.models import User 
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
    # Filtros avanzados
    filterset_fields = {
        'propiedad': ['exact'],
        'usuario': ['exact'],
        'usuario__username': ['icontains'],
        'usuario__email': ['icontains'],
        'usuario__first_name': ['icontains'],
        'usuario__last_name': ['icontains'],
    }
    search_fields = ['usuario__username', 'usuario__email', 'usuario__first_name', 'usuario__last_name', 'propiedad__numero']
    ordering_fields = ['usuario__username', 'usuario__date_joined']
    ordering = ['usuario__username']

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



@extend_schema(
    tags=["Auth"],
    summary="Registro de usuarios",
    description="Crea un usuario nuevo.",
    request=RegistroSerializer,
    responses={
        201: OpenApiResponse(response=RegistroSerializer, description="Usuario creado"),
        400: OpenApiResponse(description="Datos inválidos"),
    },
)
class RegistroView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        # --- ¡ESTA ES LA CORRECCIÓN! ---
        # Usamos RegistroSerializer en lugar de UserSerializer
        serializer = RegistroSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            # Devolvemos solo los datos seguros, no la contraseña
            user_data = serializer.data
            user_data.pop('password', None) 
            return Response(user_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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


# seguridad/views.py

# ... (importaciones y otras vistas) ...

# ========= VISTA FINAL PARA LA CÁMARA DE IA (CON NOTIFICACIONES) =========
# usuarios/views.py

# ... (otras vistas) ...
# usuarios/views.py

# ... (otras vistas) ...

# ========= VISTA PARA REGISTRO FACIAL =========

class RegistrarRostroView(APIView):
    """
    Endpoint para que un usuario autenticado suba su foto
    y la registre en el sistema de reconocimiento facial.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser] # Para aceptar subida de archivos

    def post(self, request, *args, **kwargs):
        # 1. Validar que se haya enviado un archivo de imagen
        if 'foto' not in request.FILES:
            return Response({"error": "No se ha proporcionado ninguna foto."}, status=status.HTTP_400_BAD_REQUEST)

        foto = request.FILES['foto']
        image_bytes = foto.read()

        # 2. Inicializar el cliente de AWS Rekognition
        try:
            rekognition_client = boto3.client('rekognition')
            collection_id = getattr(settings, 'AWS_REKOGNITION_COLLECTION_ID', None)
            if not collection_id:
                raise ValueError("ID de colección de AWS no configurado en settings.py")
        except Exception as e:
            return Response({"error": f"Error de configuración de AWS: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 3. Enviar la foto a AWS para que la indexe
        try:
            response = rekognition_client.index_faces(
                CollectionId=collection_id,
                Image={'Bytes': image_bytes},
                ExternalImageId=str(request.user.id), # Asociamos la cara al ID del usuario
                MaxFaces=1,
                QualityFilter="AUTO",
                DetectionAttributes=['DEFAULT']
            )

            if not response['FaceRecords']:
                return Response({"error": "No se detectó ningún rostro en la imagen."}, status=status.HTTP_400_BAD_REQUEST)

            face_record = response['FaceRecords'][0]
            face_id = face_record['Face']['FaceId']

            # 4. Guardar el FaceId en el perfil del residente
            residente, created = Residente.objects.get_or_create(usuario=request.user)
            residente.face_id_aws = face_id
            residente.save()

            return Response({
                "detail": "Rostro registrado exitosamente.",
                "faceId": face_id
            }, status=status.HTTP_201_CREATED)

        except rekognition_client.exceptions.InvalidParameterException:
            return Response({"error": "La imagen proporcionada no es válida o no contiene un rostro claro."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Error al procesar la imagen con AWS: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


from .serializers import ResidenteReadSerializer # Asegúrate que esta importación esté
from .models import Residente
from rest_framework.permissions import IsAuthenticated

class PerfilUsuarioView(generics.RetrieveAPIView):
    """
    Devuelve el perfil de residente del usuario autenticado.
    """
    serializer_class = ResidenteReadSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Busca el perfil de Residente asociado al usuario que hace la petición
        try:
            return Residente.objects.get(usuario=self.request.user)
        except Residente.DoesNotExist:
            # Si no existe un perfil de Residente, crear uno básico
            return Residente.objects.create(
                usuario=self.request.user,
                rol='otro'  # Rol por defecto
            )
# seguridad/views.py

# ... (tus otras vistas) ...

# ========= VISTA PARA VERIFICACIÓN FACIAL EN TIEMPO REAL =========

class CrearAdminView(APIView):
    """
    Endpoint TEMPORAL y de un solo uso para crear el primer superusuario.
    ¡¡¡ELIMINAR DESPUÉS DE USAR!!!
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # Comprueba si ya existe un superusuario para evitar crear más.
        if User.objects.filter(is_superuser=True).exists():
            return Response(
                {"error": "Ya existe un administrador. Este endpoint ha sido desactivado."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Se requiere 'username' y 'password'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Crea el superusuario
            User.objects.create_superuser(username=username, password=password)
            return Response(
                {"mensaje": f"Superusuario '{username}' creado exitosamente. Por favor, elimina este endpoint ahora."},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
